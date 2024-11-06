from typing import List, Dict, Any
from pydantic import Field
from workflow.db_app.initialization.modules.init_module import InitializationModule

class AdvTasksModule(InitializationModule):
    """This module defines the advanced tasks (img gen, tts, embeddings), their agents, parameters and prompts."""
    name: str = "adv_tasks"
    dependencies: List[str] = ["base", "base_chat"]
    data: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

adv_tasks_module = AdvTasksModule(
    data = {
        "parameters": [
            {
                "key": "input_parameter",
                "type": "string",
                "description": "The input text to get embeddings for. Can be a string or an array of strings."
            },
            {
                "key": "prompt_retrieval_parameter",
                "type": "string",
                "description": "The prompt to retrieve similar embeddings for."
            },
            {
                "key": "sumilarity_threshold_parameter",
                "type": "number",
                "description": "The threshold for the similarity of the embeddings."
            },
            {
                "key": "prompt_img_gen",
                "type": "string",
                "description": "The prompt to generate an image from."
            },
            {
                "key": "n_parameter",
                "type": "integer",
                "description": "The number of images to generate.",
            },
            {
                "key": "size_parameter",
                "type": "string",
                "description": "The size of the generated images.",
            },
            {
                "key": "quality_parameter",
                "type": "string",
                "description": "The quality of the image generation.",
            },
            {
                "key": "text_parameter",
                "type": "string",
                "description": "The text to convert to speech."
            },
            {
                "key": "voice_parameter",
                "type": "string",
                "description": "The voice to use for the speech.",
                "default": "nova"
            },
            {
                "key": "voice_bark_parameter",
                "type": "string",
                "description": "The voice to use for the speech.",
                "default": "v2/en_speaker_6"
            },
            {
                "key": "speed_parameter",
                "type": "number",
                "description": "The speed of the speech."
            },
        ],
        "agents": [
            {
                "key": "oai_agent",
                "name": "oai_agent",
                "system_message": "default_system_message",
                "models": {
                    "embeddings": "oai_embedding_large",
                    "img_gen": "Dall-E-3",
                    "tts": "tts-1",
                },
                "has_code_exec": 0,
                "has_tools": 0,
                "max_consecutive_auto_reply": 1,
            },
            {
                "key": "pixart_gen_agent",
                "name": "pixart_gen_agent",
                "system_message": "default_system_message",
                "models": {
                    "img_gen": "pixart_sigma_model",
                },
                "has_code_exec": 0,
                "has_tools": 0,
                "max_consecutive_auto_reply": 1,
            },
            {
                "key": "bark_tts_agent",
                "name": "bark_tts_agent",
                "system_message": "default_system_message",
                "models": {
                    "tts": "bark_large",
                },
                "has_code_exec": 0,
                "has_tools": 0,
                "max_consecutive_auto_reply": 1,
            },
            {
                "key": "groq_tts_agent",
                "name": "groq_tts_agent",
                "system_message": "default_system_message",
                "models": {
                    "tts": "groq_llama_3_2_11b_vision",
                },
                "has_code_exec": 0,
                "has_tools": 0,
                "max_consecutive_auto_reply": 1,
            },
            {
                "key": "image_gen_gemini_agent",
                "name": "image_gen_gemini_agent",
                "system_message": "default_system_message",
                "models": {
                    "img_gen": "gemini_img_gen_imagen_3",
                },
                "has_code_exec": 0,
                "has_tools": 0,
                "max_consecutive_auto_reply": 1,
            }
        ],
        "tasks": [
            {
                "key": "embedding_task",
                "task_type": "EmbeddingTask",
                "task_name": "embedding_task",
                "agent": "oai_agent",
                "task_description": "Generates embeddings for the input text",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "input": "input_parameter",
                    },
                    "required": ["input"]
                },
                "required_apis": ["embeddings"]
            },
            {
                "key": "retrieval_task",
                "task_type": "RetrievalTask",
                "task_name": "retrieval_task",
                "agent": "oai_agent",
                "task_description": "Retrieves similar embeddings for the input text",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_retrieval_parameter",
                        "max_results": "max_results_parameter",
                        "sumilarity_threshold": "sumilarity_threshold_parameter",
                    },
                    "required": ["prompt"]
                },
                "required_apis": ["embeddings"]
            },
            {
                "key": "image_gen_task",
                "task_type": "GenerateImageTask",
                "task_name": "image_gen_task_dall_e",
                "agent": "oai_agent",
                "task_description": "Generates an image from the input text",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_img_gen",
                        "n": "n_parameter",
                        "size": "size_parameter",
                        "quality": "quality_parameter"
                    },
                    "required": ["prompt"]
                },
                "required_apis": ["img_generation"],
            },
            {
                "key": "image_gen_task_pixart",
                "task_type": "GenerateImageTask",
                "task_name": "image_gen_task_pixart",
                "agent": "pixart_gen_agent",
                "task_description": "Generates an image from the input text",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_img_gen",
                        "n": "n_parameter",
                        "size": "size_parameter",
                        "quality": "quality_parameter"
                    },
                    "required": ["prompt"]
                },
                "required_apis": ["img_generation"],
            },
            {
                "key": "image_gen_task_gemini",
                "task_type": "GenerateImageTask",
                "task_name": "image_gen_task_gemini",
                "agent": "image_gen_gemini_agent",
                "task_description": "Generates an image from the input text",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "prompt": "prompt_img_gen",
                        "n": "n_parameter",
                        "size": "size_parameter",
                        "quality": "quality_parameter"
                    },
                    "required": ["prompt"]
                },
                "required_apis": ["img_generation"],
            },
            {
                "key": "tts_task",
                "task_type": "TextToSpeechTask",
                "task_name": "tts_task",
                "agent": "oai_agent",
                "task_description": "Converts text to speech using the OpenAI TTS API",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "text": "text_parameter",
                        "voice": "voice_parameter",
                        "speed": "speed_parameter"
                    },
                    "required": ["text"]
                },
                "required_apis": ["text_to_speech"]
            },
            {
                "key": "groq_tts_task",
                "task_type": "TextToSpeechTask",
                "task_name": "groq_tts_task",
                "agent": "groq_tts_agent",
                "task_description": "Converts text to speech using the Groq TTS API",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "text": "text_parameter",
                        "voice": "voice_parameter",
                        "speed": "speed_parameter"
                    },
                    "required": ["text"]
                },
                "required_apis": ["text_to_speech"]
            },
            {
                "key": "bark_tts_task",
                "task_type": "TextToSpeechTask",
                "task_name": "bark_tts_task",
                "agent": "bark_tts_agent",
                "task_description": "Converts text to speech using the Bark TTS API",
                "input_variables": {
                    "type": "object",
                    "properties": {
                        "text": "text_parameter",
                        "voice": "voice_bark_parameter",
                        "speed": "speed_parameter"
                    },
                    "required": ["text"]
                },
                "required_apis": ["text_to_speech"]
            }
        ],
    }
)
