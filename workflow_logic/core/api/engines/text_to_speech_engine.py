import base64, re
from pydantic import Field
from openai import AsyncOpenAI
from workflow_logic.core.data_structures import ModelConfig, ApiType, FileContentReference, MessageDict, ContentType, FileType, References, FunctionParameters, ParameterDefinition
from workflow_logic.core.api.engines.api_engine import APIEngine
from workflow_logic.util import LOGGER

class OpenAITextToSpeechEngine(APIEngine):
    input_variables: FunctionParameters = Field(
        default=FunctionParameters(
            type="object",
            properties={
                "input": ParameterDefinition(
                    type="string",
                    description="The text to convert to speech."
                ),
                "voice": ParameterDefinition(
                    type="string",
                    description="The voice to use for the speech.",
                    default="alloy"
                ),
                "speed": ParameterDefinition(
                    type="number",
                    description="The speed of the speech.",
                    default=1.0
                ),
            },
            required=["input"]
        )
    )
    required_api: ApiType = Field(ApiType.LLM_MODEL, title="The API engine required")

    def generate_filename(self, input: str, model: str, voice: str) -> str:
        """
        Generate a descriptive filename based on the input text, model, and voice.
        """
        # Sanitize and truncate the input text for the filename
        sanitized_input = re.sub(r'[^\w\s-]', '', input.lower())
        truncated_input = ' '.join(sanitized_input.split()[:5])  # Take first 5 words
        
        # Construct the filename
        filename = f"{truncated_input}_{model}_{voice}.mp3"
        
        # Replace spaces with underscores and ensure it's not too long
        filename = filename.replace(' ', '_')[:100]  # Limit to 100 characters
        
        return filename

    async def generate_api_response(self, api_data: ModelConfig, input: str, voice: str = "alloy", speed: float = 1.0) -> References:
        """
        Converts text to speech using OpenAI's API and creates a FileContentReference.
        Args:
            api_data (ModelConfig): Configuration data for the API (e.g., API key, base URL).
            input (str): The text to convert to speech.
            model (str): The name of the text-to-speech model to use.
            voice (str): The voice to use for the speech.
            output_filename (Optional[str]): The filename for the generated audio file. If None, a descriptive name will be generated.
        Returns:
            References: A message dict containing information about the generated audio file.
        """
        client = AsyncOpenAI(
            api_key=api_data.api_key,
            base_url=api_data.base_url
        )
        model = api_data.model
        try:
            response = await client.audio.speech.create(
                model=model,
                voice=voice,
                input=input,
                speed=float(speed)
            )
           
            # Get the raw audio data
            audio_data = response.read()
            
            # Generate filename if not provided
            output_filename = self.generate_filename(input, model, voice)
            
            creation_metadata = {
                    "model": model,
                    "voice": voice,
                    "input_text_length": len(input)
                }
            # Create a FileContentReference
            file_reference = FileContentReference(
                filename=output_filename,
                type=FileType.AUDIO,
                content=base64.b64encode(audio_data).decode('utf-8'),
                transcript=MessageDict(
                    role='tool', 
                    content=f"Speech generated by model {model}. /nInput: '{input}' /nVoice: {voice}", 
                    type=ContentType.TEXT, 
                    generated_by='tool', 
                    creation_metadata=creation_metadata)
            )
            return References(files=[file_reference])

        except Exception as e:
            import traceback
            LOGGER.error(f"Error generating speech: {traceback.format_exc()}")
            raise Exception(f"Error in OpenAI text-to-speech API call: {str(e)}")