from pydantic import BaseModel, Field
from typing import List, Tuple, Optional, Union
import json, logging
from workflow_logic.util.utils import LLMConfig
from workflow_logic.util.task_utils import MessageDict, TaskResponse
from workflow_logic.core.agent import AliceAgent
from workflow_logic.core.tasks import AliceTask
from autogen.agentchat import ConversableAgent

default_system_message = {
    "name": "alice_default",
    "content": "You are Alice, an AI personal assistant powered by a suite of tools. Your job is to assist your user to the best of your abilities."
}

class AliceChat(BaseModel):
    id: str = Field(default="", description="The unique ID of the chat conversation, must match the ID in the database", alias="_id")
    name: str = Field("New Chat", description="The name of the chat conversation")
    messages: List[MessageDict] = Field(..., description="List of messages in the chat conversation")
    alice_agent: AliceAgent = Field(
        default = AliceAgent(
            name="Alice",
            system_message=default_system_message,
        ), 
        description="The Alice agent object. Default is base Alice Agent.")
    functions: Optional[List[AliceTask]] = Field([], description="List of functions to be registered with the agent")
    executor: AliceAgent = Field(
        default = AliceAgent(name="executor_agent", 
                             system_message={"name": "executor_agent", "content":"Executor Agent. Executes the code and returns the result."}, 
                             autogen_class="UserProxyAgent", 
                             code_execution_config=True, 
                             default_auto_reply=""),
        description="The executor agent object. Default is base Alice Agent.")
    llm_config: Optional[LLMConfig] = Field(None, description="The configuration for the LLM agent")
    task_responses: List[TaskResponse] = Field([], description="List of task responses in the chat conversation")

    def generate_response(self, new_messages: Optional[List[MessageDict]] = None, task_responses: Optional[List[TaskResponse]]=None , recursed_already: bool = False) -> Tuple[List[MessageDict], Optional[List[TaskResponse]]]:
            # Initialize new_messages if it's None
        if new_messages is None:
            new_messages = []
        if task_responses is None:
            task_responses = []
        llm_agent, executor = self.get_agents()
        response_1 = llm_agent.generate_reply(self.messages)
        if not response_1:
            raise ValueError("No response generated by LLM agent.")
        print(f'response_1: {response_1}')
        if isinstance(response_1, str):    
            message_1 = MessageDict(content=response_1, role="assistant", generated_by="llm", assistant_name=llm_agent.name, type="text")
            self.messages.append(message_1) # STORE IN DB?
            new_messages.append(message_1)
            return new_messages
        elif isinstance(response_1, dict) and (response_1.get("function_call") or response_1.get("tool_calls")):
            if recursed_already:
                print(f'Error: Recursion detected. ')
            if response_1.get("tool_calls"):
                for tool_call in response_1["tool_calls"]:
                    tool_function = tool_call["function"]
                    function_name = tool_function.get("name")
                    args = tool_function.get("arguments", "{}")
                    print(f'function_name: {function_name} \n args: {args} argstype {type(args)}')
                    if not function_name:
                        raise ValueError("Function name not found in tool call.")
                    tool_call_gen_message = MessageDict(content=f"Calling function {function_name} with arguments: {args}", role="assistant", generated_by="llm", assistant_name=llm_agent.name, type="text")
                    self.messages.append(tool_call_gen_message) # STORE IN DB?
                    new_messages.append(tool_call_gen_message)
                    if function_name not in executor._function_map:
                        raise ValueError(f"Function {function_name} not found in executor function map.")
                    callable = executor._function_map.get(function_name)
                    input_string = executor._format_json_str(args)
                    response_2, success = self.execute_tool_call(callable, input_string, function_name)
                    print(f'response_2: {response_2} \n success: {success}')
                    if isinstance(response_2, TaskResponse):
                        self.task_responses.append(response_2) # Store in the DB!
                        task_responses.append(response_2)
                        message_2 = MessageDict(content=str(response_2), role="tool", generated_by="tool", assistant_name=executor.name, type="TaskResponse", step=response_2.task_name)
                        self.messages.append(message_2) # STORE IN DB?
                        new_messages.append(message_2)
                    elif isinstance(response_2, str):
                        message_2 = MessageDict(content=response_2, role="tool", generated_by="tool", assistant_name=executor.name, type="text", step=function_name)
                        self.messages.append(message_2)
                        new_messages.append(message_2)
                if not recursed_already:
                    return self.generate_response(new_messages=new_messages, recursed_already=True)
            else:
                content = f'Error: Function call / dict response not supported: {response_1}'
                message_1 = MessageDict(content=content, role="assistant", generated_by="llm", assistant_name=llm_agent.name, type="text")
                self.messages.append(message_1) # STORE IN DB?
                new_messages.append(message_1)
        return new_messages, task_responses 
        # Or store them all together? I'm inclined to always store to avoid errors preventing long chains of messages from not being stored bc of errors

    def execute_tool_call(self, callable: callable, input_string, function_name: str) -> Tuple[Union[TaskResponse, str], bool]:
        print(f'input type: {type(input_string)}')
        is_exec_success = False
        try:
            arguments = json.loads(input_string)
        except json.JSONDecodeError as e:
            arguments = None
            content = f"Error: {e}\n You argument should follow json format."

        # Try to execute the function
        if arguments is not None:
            logging.info(f"\n>>>>>>>> EXECUTING FUNCTION {function_name}...")
            try:
                content = callable(**arguments)
                is_exec_success = True
            except Exception as e:
                content = f"Error: {e}"
        return content, is_exec_success

    def get_autogen_agent(self) -> ConversableAgent:
        return self.alice_agent.get_autogen_agent(llm_config=self.llm_config.model_dump() if self.llm_config else None)
    
    def get_default_executor(self) -> ConversableAgent:
        return self.executor.get_autogen_agent()
    
    def get_agents(self, execution_history: List = []) -> Tuple[ConversableAgent, ConversableAgent]:
        if self.functions:
            return self.get_agents_with_functions(execution_history=execution_history)
        else:
            return self.get_autogen_agent(), self.get_default_executor()

    def get_agents_with_functions(self, execution_history: List = []) -> Tuple[ConversableAgent, ConversableAgent]:
        for task in self.functions:
            self.inject_llm_config(task)
            task_function = task.get_function(execution_history=execution_history)
            llm_agent = self.get_autogen_agent()
            llm_agent.update_tool_signature(task_function["tool_dict"], is_remove=False)
            executor = self.get_default_executor()
            executor.register_function(task_function["function_map"])
            print(f'function map: {executor.function_map}')
        return llm_agent, executor
    
    def inject_llm_config(self, task: AliceTask) -> AliceTask:
        if task.agent_id and not task.agent_id.llm_config:
            task.agent_id.llm_config = self.llm_config.model_dump() if self.llm_config else None
        return task