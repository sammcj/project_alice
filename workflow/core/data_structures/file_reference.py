from __future__ import annotations
import base64, io, magic, os
from typing import Union, BinaryIO, Optional
from pydantic import Field, field_validator
from PIL import Image
from workflow.core.data_structures.base_models import BaseDataStructure, FileType
from workflow.core.data_structures.message import MessageDict
from workflow.util import LOGGER

class FileReference(BaseDataStructure):
    id: Optional[str] = Field(None, description="The unique identifier for the file reference", alias="_id")
    filename: str = Field(..., description="The name of the file reference")
    type: FileType = Field(..., description="The type of the file reference")
    storage_path: str = Field(..., description="The path to the file in the shared volume")
    transcript: Optional[MessageDict] = Field(None, description="The transcript / description of the file content")

    @field_validator('transcript')
    def validate_transcript(cls, v):
        if v is None:
            return v
        if isinstance(v, MessageDict):
            return v
        if isinstance(v, dict):
            return MessageDict(**v)
        raise ValueError(f"Invalid type for transcript: {type(v)}. Expected MessageDict, dict, or None.")
    
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        LOGGER.debug(f"Data after super().model_dump: {data}")
        if self.transcript:
            data['transcript'] = self.transcript.model_dump(*args, **kwargs)
        LOGGER.debug(f"Data after processing transcript: {data}")
        return data

    class Config:
        populate_by_name = True
        
    def __str__(self) -> str:
        return self.get_content_string()

    def get_content_string(self, max_chars: int = 1000) -> str:
        """
        Retrieves the content of the file as a string, with contextual information.
        
        For non-text files, it uses the transcript if available.
        For text files, it reads the content directly from the file.
        
        Args:
            max_chars (int): Maximum number of characters to return for text files.
        
        Returns:
            str: A string containing file information and content.
        """
        file_info = f"\n\nFile: {self.filename}\n\nType: {self.type.value}"
        
        if self.type == FileType.FILE:
            try:
                with open(self.storage_path, 'r') as file:
                    content = file.read(max_chars)
                return f"{file_info}Content (first {max_chars} characters):\n{content}"
            except Exception as e:
                LOGGER.error(f"Error reading text file {self.filename}: {str(e)}")
                return f"{file_info}Error: Unable to read file content"
        elif self.transcript:
            model_name = self.transcript.creation_metadata.get('model', 'Unknown') if self.transcript.creation_metadata else 'Unknown'
            return f"{file_info}Transcript (generated by {model_name}):\n\n{self.transcript.content}"
        else:
            return f"{file_info}No transcript available for this file."

    @property
    def file_extension(self) -> str:
        """Returns the file extension."""
        return os.path.splitext(self.filename)[1]

class FileContentReference(FileReference):
    storage_path: Optional[str] = Field(None, description="The path to the file in the shared volume")
    content: str = Field(..., description="The base64 encoded content of the file")

def generate_file_content_reference(file: Union[BinaryIO, io.BytesIO], filename: str) -> FileContentReference:
    # Ensure we're at the start of the file
    file.seek(0)
    
    # Read the first 2048 bytes for MIME type detection
    file_start = file.read(2048)
    file.seek(0)  # Reset file position

    # Use magic to get the MIME type
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file_start)

    # Determine content type based on MIME type
    content_type = FileType.FILE
    if file_mime.startswith('image/'):
        content_type = FileType.IMAGE
    elif file_mime.startswith('audio/'):
        content_type = FileType.AUDIO
    elif file_mime.startswith('video/'):
        content_type = FileType.VIDEO

    # Verify that the file extension matches the MIME type
    _, file_extension = os.path.splitext(filename)
    extension_mime_map = {
        '.txt': 'text/plain',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/x-wav',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo'
    }

    if file_extension.lower() in extension_mime_map:
        expected_mime = extension_mime_map[file_extension.lower()]
        if not file_mime.startswith(expected_mime):
            print(f"Warning: File extension '{file_extension}' does not match the detected MIME type '{file_mime}'")

    # Read and encode file content
    file_content = file.read()
    base64_content = base64.b64encode(file_content).decode('utf-8')

    # Create and return FileContentReference
    return FileContentReference(
        filename=filename,
        type=content_type,
        content=base64_content
    )

def get_file_content(file_reference: FileReference, max_pixels: int = 1024*1024, max_file_size: int = 20*1024*1024) -> Union[str, bytes]:
    """
    Helper method to get the content of a file from a FileReference or its subclasses.
   
    Args:
    file_reference (FileReference): The file reference object.
    max_pixels (int): Maximum number of pixels for images (default: 1024*1024).
    max_file_size (int): Maximum file size in bytes (default: 20MB).
   
    Returns:
    Union[str, bytes]: The content of the file as a string for text files, or bytes for binary files.
   
    Raises:
    FileNotFoundError: If the file is not found at the storage_path.
    IOError: If there's an error reading the file.
    ValueError: If the file_reference is invalid or the content can't be processed.
    """
    try:
        LOGGER.debug(f"Processing file: {file_reference.filename}, Type: {file_reference.type}")
        content = None
        if isinstance(file_reference, FileContentReference) and file_reference.content:
            LOGGER.debug('FileContentReference with content found')
            content = base64.b64decode(file_reference.content)
        elif file_reference.storage_path:
            LOGGER.debug(f'FileReference with storage_path found: {file_reference.storage_path}')
            file_path = file_reference.storage_path
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found at {file_path}")
           
            with open(file_path, 'rb') as file:
                content = file.read()
        else:
            raise ValueError("Invalid FileReference: No content or valid storage_path provided")

        # Process image files
        if file_reference.type == FileType.IMAGE:
            LOGGER.debug("Processing image file")
            image = Image.open(io.BytesIO(content))
            LOGGER.debug(f"Original image size: {image.size}, Format: {image.format}")
            
            # Calculate scaling factor
            current_pixels = image.width * image.height
            if current_pixels > max_pixels:
                scale_factor = (max_pixels / current_pixels) ** 0.5
                new_width = int(image.width * scale_factor)
                new_height = int(image.height * scale_factor)
                
                LOGGER.info(f"Scaling image from {image.width}x{image.height} to {new_width}x{new_height}")
                image = image.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert back to bytes
                img_byte_arr = io.BytesIO()
                image_format = image.format if image.format else 'PNG'  # Default to PNG if format is unknown
                LOGGER.debug(f"Saving image in format: {image_format}")
                image.save(img_byte_arr, format=image_format)
                content = img_byte_arr.getvalue()

        # Check file size after potential rescaling
        if len(content) > max_file_size:
            raise ValueError(f"File size ({len(content)} bytes) exceeds the maximum allowed size of {max_file_size} bytes")

        # Return content based on file type
        if file_reference.type == FileType.FILE:
            return content.decode('utf-8')
        else:
            return content

    except FileNotFoundError as e:
        LOGGER.error(f"File not found: {str(e)}")
        raise
    except IOError as e:
        LOGGER.error(f"Error reading file: {str(e)}")
        raise
    except Exception as e:
        LOGGER.error(f"Error processing FileReference: {str(e)}", exc_info=True)
        raise ValueError(f"Error processing FileReference: {str(e)}")