import requests, aiohttp, asyncio, json
from aiohttp import ClientError
from bson import ObjectId
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from workflow_logic.util.logging_config import LOGGER
from workflow_logic.core.communication import DatabaseTaskResponse, MessageDict
from workflow_logic.core.api.api_utils import available_task_types
from workflow_logic.util.const import BACKEND_PORT, HOST, ADMIN_TOKEN
from workflow_logic.core import AliceAgent, AliceChat, Prompt, AliceModel, AliceTask, DatabaseTaskResponse
from workflow_logic.core.api import API
from workflow_logic.util import User
from workflow_logic.core.api.api_utils import  EntityType

class BackendAPI(BaseModel):
    base_url: Literal[f"http://{HOST}:{BACKEND_PORT}/api"] = Field(f"http://{HOST}:{BACKEND_PORT}/api", description="The base URL of the backend API", frozen=True)
    user_token: str = Field(ADMIN_TOKEN, description="The admin token for the backend API")
    available_task_types: list[AliceTask] = Field(available_task_types, frozen=True, description="The available task types")
    collection_map: Dict[EntityType, str] = Field(default_factory=lambda: {
        "users": "users",
        "models": "models",
        "prompts": "prompts",
        "agents": "agents",
        "tasks": "tasks",
        "chats": "chats", 
        "parameters": "parameters",
        "task_responses": "taskresults",
        "apis": "apis"
    }, description="Map of entity types to collection names")

    class Config:
        arbitrary_types_allowed = True
        protected_namespaces = ()
        json_encoders = {ObjectId: str}

    @property
    def task_types(self) -> Dict[str, AliceTask]:
        return {task.__name__: task for task in self.available_task_types}
    
    async def initialize_db_app(self):
        try:
            if self.user_token:
                validate = self.validate_token(self.user_token)
                if validate.get("valid"):
                    return True
        except Exception as e:
            LOGGER.error(f"Error in initialize_libraries: {e}")
            raise

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.user_token}"
        }

    # Function to preprocess the data
    async def preprocess_data(self, data):
        if isinstance(data, dict):
            return {k: await self.preprocess_data(v) for k, v in data.items() if v or v == 0}
        elif isinstance(data, list):
            return [await self.preprocess_data(item) for item in data if item or item == 0]
        else:
            return data if data or data == 0 else None
        
    async def get_prompts(self, prompt_id: Optional[str] = None) -> Dict[str, Prompt]:
        if prompt_id is None:
            url = f"{self.base_url}/prompts"
        else:
            url = f"{self.base_url}/prompts/{prompt_id}"
        headers = self._get_headers()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response is None:
                        raise ValueError(f"Failed to get a response from {url}")
                    print(f'RESPONSE :{response}')
                    response.raise_for_status()
                    prompts = await response.json()

                    if isinstance(prompts, list):
                        print(f'PROMPTS: {prompts}')
                        prompts = [await self.preprocess_data(prompt) for prompt in prompts]
                        return {prompt["_id"]: Prompt(**prompt) for prompt in prompts}
                    else:
                        prompts = await self.preprocess_data(prompts)
                        return {prompts["_id"]: Prompt(**prompts)}
            except aiohttp.ClientError as e:
                LOGGER.error(f"Error retrieving prompts: {e}")
                return {}
            except Exception as e:
                LOGGER.error(f"Unexpected error retrieving prompts: {e}")
                return {}
            
    async def get_users(self, user_id: Optional[str] = None) -> Dict[str, User]:
        if user_id is None:
            url = f"{self.base_url}/users"
        else:
            url = f"{self.base_url}/users/{user_id}"
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    users = await response.json()
                    
                    if isinstance(users, list):
                        users = [await self.preprocess_data(user) for user in users]
                        return {user["_id"]: User(**user) for user in users}
                    else:
                        users = await self.preprocess_data(users)
                        return {users["_id"]: User(**users)}
            except aiohttp.ClientError as e:
                print(f"Error retrieving users: {e}")
                return {}

    async def get_agents(self, agent: Optional[str] = None) -> Dict[str, AliceAgent]:
        if agent is None:
            url = f"{self.base_url}/agents"
        else:
            url = f"{self.base_url}/agents/{agent}"
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response is None:
                        raise ValueError(f"Failed to get a response from {url}")
                    print(f'RESPONSE :{response}')
                    response.raise_for_status()
                    agents = await response.json()
                    
                    if isinstance(agents, list):
                        preprocessed_agents = [await self.preprocess_data(agent) for agent in agents]
                        return {agent["_id"]: AliceAgent(**agent) for agent in preprocessed_agents}
                    else:
                        preprocessed_agent = await self.preprocess_data(agents)
                        return {agents["_id"]: AliceAgent(**preprocessed_agent)}
            except aiohttp.ClientError as e:
                print(f"Error retrieving agents: {e}")
                return {}

    async def get_tasks(self, task_id: Optional[str] = None) -> Dict[str, AliceTask]:
        if task_id is None:
            url = f"{self.base_url}/tasks"
        else:
            url = f"{self.base_url}/tasks/{task_id}"
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response is None:
                        raise ValueError(f"Failed to get a response from {url}")
                    response.raise_for_status()
                    tasks = await response.json()
                    
                    if isinstance(tasks, list):
                        tasks = [await self.preprocess_data(task) for task in tasks]
                        return {task["_id"]: await self.task_initializer(task) for task in tasks}
                    else:
                        tasks = await self.preprocess_data(tasks)
                        return {tasks["_id"]: await self.task_initializer(tasks)}
            except aiohttp.ClientError as e:
                print(f"Error retrieving tasks: {e}")
                return {}

    async def get_models(self, model_id: Optional[str] = None) -> Dict[str, AliceModel]:
        if model_id is None:
            url = f"{self.base_url}/models"
        else:
            url = f"{self.base_url}/models/{model_id}"
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response is None:
                        raise ValueError(f"Failed to get a response from {url}")
                    response.raise_for_status()
                    models = await response.json()
                    
                    if isinstance(models, list):
                        models = [await self.preprocess_data(model) for model in models]
                        return {model['_id']: AliceModel(**model) for model in models}
                    else:
                        models = await self.preprocess_data(models)
                        return {models['_id']: AliceModel(**models)}
            except aiohttp.ClientError as e:
                print(f"Error retrieving models: {e}")
                return {}
            
    async def get_apis(self, api_id: Optional[str] = None) -> Dict[str, API]:
        if api_id is None:
            url = f"{self.base_url}/apis"
        else:
            url = f"{self.base_url}/apis/{api_id}"
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    apis = await response.json()
                    
                    if isinstance(apis, list):
                        apis = [await self.preprocess_data(api) for api in apis]
                        return {api["_id"]: API(**api) for api in apis}
                    else:
                        apis = await self.preprocess_data(apis)
                        return {apis["_id"]: API(**apis)}
            except aiohttp.ClientError as e:
                print(f"Error retrieving APIs: {e}")
                return {}
            
    async def update_api_health(self, api_id: str, health_status: str) -> bool:
        url = f"{self.base_url}/apis/{api_id}"
        headers = self._get_headers()
        data = {"health_status": health_status}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(url, json=data, headers=headers) as response:
                    response.raise_for_status()
                    return True
            except aiohttp.ClientError as e:
                print(f"Error updating API health: {e}")
                return False
    
    async def task_initializer(self, task: dict) -> AliceTask:
        if not task["task_type"] in self.task_types:
            raise ValueError(f"Task type {task['task_type']} not found in available task types.")
        
        if "tasks" in task and isinstance(task["tasks"], dict):
            # Use asyncio.gather to initialize subtasks concurrently
            subtasks = await asyncio.gather(*[
                self.task_initializer(subtask) 
                for subtask in task["tasks"].values()
            ])
            task["tasks"] = {
                subtask["_id"]: initialized_subtask 
                for subtask, initialized_subtask in zip(task["tasks"].values(), subtasks)
            }
    
        # Assuming the task_types constructors are not async
        return self.task_types[task["task_type"]](**task)
    
    async def get_chats(self, chat_id: Optional[str] = None) -> Dict[str, AliceChat]:
        if chat_id is None:
            url = f"{self.base_url}/chats"
        else:
            url = f"{self.base_url}/chats/{chat_id}"
        headers = self._get_headers()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    chats = await response.json()
                    print(f'Chats response: {chats}')
                    
                    if isinstance(chats, list):
                        chats = [await self.preprocess_data(chat) for chat in chats]
                        return {chat["_id"]: await self.populate_chat(chat) for chat in chats}
                    else:
                        chats = await self.preprocess_data(chats)
                        return {chats['_id']: await self.populate_chat(chats)}
            except aiohttp.ClientError as e:
                print(f"Error retrieving chats: {e}")
                return {}
        
    async def populate_chat(self, chat: dict) -> AliceChat:
        print(f'Chat: {chat}')

        if 'functions' in chat and chat['functions']:
            processed_functions = []
            for function in chat['functions']:
                try:
                    task = await self.task_initializer(function)
                    if not isinstance(task, AliceTask):
                        print(f"Warning: task_initializer returned non-AliceTask object for function {function.get('task_name', 'Unknown')}")
                        continue
                    processed_functions.append(task)
                except Exception as e:
                    print(f"Error processing function {function.get('task_name', 'Unknown')}: {str(e)}")
    
            chat['functions'] = processed_functions

        # Ensure all required fields are present in messages
        for message in chat.get('messages', []):
            if 'task_responses' not in message:
                message['task_responses'] = []

        print(f'Messages: {chat["messages"]}')
        
        try:
            return AliceChat(**chat)
        except Exception as e:
            print(f"Error creating AliceChat object: {str(e)}")
            # You might want to add more detailed error handling here
            raise
    
    async def store_chat_message(self, chat_id: str, message: MessageDict) -> AliceChat:
        url = f"{self.base_url}/chats/{chat_id}/add_message"
        headers = self._get_headers()
        data = {"message": message}  # Wrap the message in a "message" key
        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, json=data, headers=headers) as response:
                    response.raise_for_status()
                    return True
        except aiohttp.ClientError as e:
            print(f"Error storing messages: {e}")
            return None

    async def store_task_response(self, task_response: DatabaseTaskResponse) -> DatabaseTaskResponse:
        url = f"{self.base_url}/taskResults"
        headers = self._get_headers()
        headers['Content-Type'] = 'application/json'
        
        # Use model_dump_json() to get a JSON string
        json_str = task_response.model_dump_json(by_alias=True)
        # Parse the JSON string back into a Python object
        data = json.loads(json_str)
        
        print(f"Data after parsing: {str(data)}...") 
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:                
                    try:
                        response.raise_for_status()
                    except aiohttp.ClientResponseError as e:
                        print(f"Response status: {response.status}")
                        response_text = await response.text()
                        print(f"Response content: {response_text}")
                        raise
                    result = await response.json()
                    print(f'Result: {result}')
                    return DatabaseTaskResponse(**result)
        except aiohttp.ClientError as e:
            print(f"Error storing DatabaseTaskResponse: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise      

    async def store_task_response_on_chat(self, task_response: DatabaseTaskResponse, chat_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chats/{chat_id}/add_task_response"
        headers = self._get_headers()
        try:
            result = await self.store_task_response(task_response)
            async with aiohttp.ClientSession() as session:
                async with session.patch(url, json={"task_response_id": result.id}, headers=headers) as response:
                    response.raise_for_status()
                    chat_result = await response.json()
                    print(f"DatabaseTaskResponse added to chat successfully: {chat_result}")
                    return chat_result
        except aiohttp.ClientError as e:
            print(f"Error storing DatabaseTaskResponse on chat: {e}")
            raise
        
    def validate_token(self, token: str) -> dict:
        url = f"{self.base_url}/users/validate"
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Attempting to validate token at URL: {url}")
        print(f"Headers: {headers}")
        try:
            response = requests.get(url, headers=headers)
            print(f"Token validation response: {response}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error validating token: {e}")
            return {"valid": False, "message": str(e)}
        
    async def create_entity_in_db(self, entity_type: EntityType, entity_data: dict) -> str:
        collection_name = self.collection_map[entity_type]
        url = f"{self.base_url}/{collection_name}"
        headers = self._get_headers()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=entity_data, headers=headers) as response:
                    if response.status == 400:
                        error_data = await response.json()
                        raise ValueError(f"Bad request when creating {entity_type}: {error_data}")
                    
                    response.raise_for_status()
                    result = await response.json()
                    print(f'Created {entity_type[:-1]}: {entity_data.get("key", entity_data.get("name", entity_data.get("email")))}')
                    print(f'Result: {result}')
                    return result
            except aiohttp.ClientResponseError as e:
                print(f"HTTP error during entity creation: {e.status} - {e.message}")
                print(f"Entity data: {entity_data}")
                raise
            except Exception as e:
                print(f"Unexpected error during entity creation: {str(e)}")
                print(f"Entity data: {entity_data}")
                raise

    async def check_existing_data(self, max_retries=3, retry_delay=1) -> bool:
        for attempt in range(max_retries):
            try:
                for collection in self.collection_map.values():
                    if collection == "users":
                        continue
                    url = f"{self.base_url}/{collection}"
                    headers = self._get_headers()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, timeout=30) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data:
                                    return True
                return False
            except (ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    print(f"Failed to check existing data after {max_retries} attempts: {str(e)}")
                    raise
                print(f"Attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)

def token_validation_middleware(api: BackendAPI):
    def middleware(request) -> dict[str, bool]:
        token = request.headers.get("Authorization")
        if not token:
            return {"valid": False, "message": "Access denied. No token provided."}

        token = token.split(" ")[1]
        validation_response = api.validate_token(token)
        if not validation_response.get("valid"):
            return {"valid": False, "message": validation_response.get("message", "Invalid token")}
        print('validation_response', validation_response)
        request.state.user_id = validation_response["user"]["id"]
        return {"valid": True}
    return middleware