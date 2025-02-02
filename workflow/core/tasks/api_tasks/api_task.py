from typing import List, Type, Dict
from pydantic import Field, model_validator
from workflow.core.api import APIEngine
from workflow.core.api import APIManager
from workflow.core.api.engines import ApiEngineMap
from workflow.core.data_structures import ApiType, ApiName
from workflow.core.data_structures import NodeResponse, References, TasksEndCodeRouting
from workflow.core.tasks.task import AliceTask
from workflow.util import get_traceback

class APITask(AliceTask):
    """
    A specialized AliceTask implementation for direct API interactions with a single, focused purpose.

    APITask provides a streamlined way to interact with external APIs by implementing a simplified
    node structure with a single 'default' node. This design is ideal for straightforward API
    operations that don't require complex workflow logic.

    Key Features:
    -------------
    * Single API Focus:
        - Each instance works with exactly one API type
        - Built-in API validation and configuration
        - Automatic routing for retry attempts

    * Simplified Node Structure:
        - Single 'default' node implementation
        - Automatic retry handling
        - Standardized error management

    * API Engine Integration:
        - Direct mapping to API engine classes
        - Automatic configuration validation
        - Consistent response formatting

    Attributes:
    -----------
    required_apis : List[ApiType]
        Must contain exactly one ApiType
        
    api_engine : Type[APIEngine]
        The class of the API engine to be used
        
    start_node : str
        Always 'default' for this implementation
        
    node_end_code_routing : TasksEndCodeRouting
        Pre-configured for single node with retry logic:
        - Exit code 0: Success, end task
        - Exit code 1: Failure, retry if attempts remain

    Example:
    --------
    ```python
    class SearchAPITask(APITask):
        required_apis = [ApiType.GOOGLE_SEARCH]
        api_engine = GoogleSearchEngine
        input_variables = FunctionParameters(
            properties={
                "query": ParameterDefinition(
                    type="string",
                    description="Search query"
                )
            },
            required=["query"]
        )
    ```

    Notes:
    ------
    1. API Validation:
        - Validates exactly one required API
        - Ensures API type matches engine capabilities
        - Verifies input variable compatibility

    2. Execution Flow:
        - Single node execution with automatic retry
        - Standardized error handling
        - Consistent response formatting

    3. Implementation:
        - No need to implement node methods
        - Can override default behavior if needed
        - Handles all basic API interaction patterns
    """
    required_apis: List[ApiType] = Field(..., min_length=1, max_length=1)
    api_engine: Type[APIEngine] = Field(None)
    start_node: str = Field(default='default', description="The name of the starting node")
    node_end_code_routing: TasksEndCodeRouting = Field(default={
        'default': {
            0: (None, False),
            1: ('default', True),
        }
    }, description="A dictionary of tasks/nodes -> exit codes and the task to route to given each exit code")

    @model_validator(mode='after')
    def validate_api_task(cls, values):
        """
        Validate the API task configuration.

        This method ensures that:
        1. Exactly one API is specified.
        2. The specified API type is valid and not LLM_MODEL.
        3. An appropriate API engine class exists for the specified API type.
        4. The task's input variables are consistent with the API engine's requirements.

        Args:
            values: The attribute values to validate.

        Returns:
            dict: The validated values.

        Raises:
            ValueError: If any validation check fails.
        """
        # Validate that there's exactly one required API
        required_apis = values.required_apis
        if len(required_apis) != 1:
            raise ValueError("APITask must have exactly one required API")

        # Validate that the API type is valid and not LLM_MODEL
        api_type = required_apis[0]
        if api_type not in ApiType.__members__.values() or api_type == ApiType.LLM_MODEL:
            raise ValueError(f"{api_type} is not a valid API type for APITask")

        # Get the correct API engine class
        api_engines_dict: Dict[ApiName, APIEngine] = ApiEngineMap.get(api_type)
        if api_engines_dict is None:
            raise ValueError(f"No API engine class found for {api_type}")

        # Retrieve the first ApiName from the API engine map
        api_engine_class = next(iter(api_engines_dict.values()))
        # Instantiate the API engine to access its input_variables
        api_engine_instance = api_engine_class()

        # Validate that the task's input variables are consistent with the API engine's requirements
        task_inputs = values.input_variables
        engine_inputs = api_engine_instance.input_variables

        for required_param in engine_inputs.required:
            if required_param not in task_inputs.properties:
                raise ValueError(f"Required parameter '{required_param}' from API engine not found in task inputs")

        values.api_engine = api_engine_class
        return values

    async def execute_default(self, execution_history: List[NodeResponse], node_responses: List[NodeResponse], **kwargs) -> NodeResponse:
        """
        Execute the default node, which performs the API interaction.

        This method retrieves the necessary API data, instantiates the appropriate
        API engine, and executes the API request. It handles both successful
        executions and errors, wrapping the result in a NodeResponse.

        Args:
            execution_history (List[NodeResponse]): The full execution history of the task.
            node_responses (List[NodeResponse]): The responses from previously executed nodes.
            **kwargs: Additional keyword arguments, including 'api_manager' and task-specific inputs.

        Returns:
            NodeResponse: A response object containing the results of the API task execution.
        """
        api_manager: APIManager = kwargs.get("api_manager")
        try:
            api_data = api_manager.retrieve_api_data(self.required_apis[0])
            api_engine = self.api_engine()  # Instantiate the API engine
            references = await api_engine.generate_api_response(api_data=api_data, **kwargs)
            return NodeResponse(
                parent_task_id=self.id,
                node_name="default",
                execution_order=len(execution_history),
                exit_code=0,
                references=references,
            )
        except Exception as e:
            error_message = f'Error: {e}\nTraceback: {get_traceback()}'
            return NodeResponse(
                parent_task_id=self.id,
                node_name="default",
                exit_code=1,
                references=References(messages=[{
                    "role": "system",
                    "content": error_message,
                    "generated_by": "system"
                }]),
                execution_order=len(execution_history)
            )