from workflow_logic.core.parameters import FunctionParameters, ParameterDefinition
from workflow_logic.core.tasks.task import AliceTask
from workflow_logic.core.tasks.agent_tasks import PromptAgentTask, CodeGenerationLLMTask, CodeExecutionLLMTask, CheckTask, AgentWithFunctions, BasicAgentTask
from workflow_logic.core.tasks.workflow import Workflow
from workflow_logic.core.tasks.api_tasks import RedditSearchTask, ExaSearchTask, WikipediaSearchTask, GoogleSearchTask, ArxivSearchTask, APITask
from typing import List

## Parameters for the CV Generation Workflow
cv_clarifications_parameters = FunctionParameters(
    type="object",
    properties={
        "inputs_job_description": ParameterDefinition(
            type="string",
            description="The job description for which the CV is being created.",
            default=None
            ),
        "inputs_user_history": ParameterDefinition(
            type="string",
            description="The user's history and experience.",
            default=None
            ),
        "inputs_additional_details": ParameterDefinition(
            type="string",
            description="Additional context or details provided by the user.",
            default=None
            ),
        "inputs_request_cover_letter": ParameterDefinition(
            type="boolean",
            description="Whether a cover letter is requested.",
            default=False
            ),
    },
    required=["inputs_job_description", "inputs_user_history", "inputs_additional_details", "inputs_request_cover_letter"]
)

user_clarifications_parameters = FunctionParameters(
    type="object",
    properties={
        "outputs_cv_clarifications_task": ParameterDefinition(
            type="string",
            description="The clarifications generated by the CV clarifications task.",
            default=None
            ),
    },
    required=["outputs_cv_clarifications_task"]
)

cv_brainstorming_parameters = cv_clarifications_parameters.model_copy()
cv_brainstorming_parameters.properties["outputs_user_answers_questions"] = user_clarifications_parameters.properties["outputs_cv_clarifications_task"]
cv_brainstorming_parameters.properties["outputs_user_answers_questions"] = ParameterDefinition(
    type="string", 
    description="The user's answers to the clarifying questions.",
    default=None
)

cv_cover_letter_parameters = cv_brainstorming_parameters.model_copy()
cv_cover_letter_parameters.properties["outputs_cv_brainstorming_task"] = ParameterDefinition(
    type="string",
    description="The brainstorming results from the CV brainstorming task.",
    default=None
)
cv_cover_letter_parameters.required.append("outputs_cv_brainstorming_task")

cv_cv_generation_parameters = cv_cover_letter_parameters.model_copy()
cv_cv_generation_parameters.properties["outputs_cv_cover_letter_task"] = ParameterDefinition(
    type="string",
    description="The cover letter generated by the CV cover letter task.",
    default=None
)
cv_cv_generation_parameters.required.append("outputs_cv_cover_letter_task")


# cv_clarifications_task = CVGenerationTask(
#     task_name="cv_clarifications_task",
#     task_description="Generate clarifying questions for the CV generation task.",
#     input_variables=cv_clarifications_parameters,
#     prompts_to_add={
#         "task_description": """## CURRENT TASK: Look at all the available data and take some time to analyze it. Create a list of (up to 5) clarifying questions to ask the user in order to ensure we can create an amazing CV for them.""",
#     }
# )
# user_clarifications_task = PromptAgentTask(
#     task_name="user_clarifications_task",
#     task_description="Asks the user to provide clarifications based on the agent's questions.",
#     input_variables=user_clarifications_parameters,
#     agent_name="user_input_agent",
#     templates={"task_template": "user_clarifications"},
#     human_input=True,
# )
# cv_brainstorming_task = CVGenerationTask(
#     task_name="cv_brainstorming_task",
#     task_description="Brainstorm ideas for the CV generation task.",
#     input_variables=cv_brainstorming_parameters,
#     prompts_to_add={
#         "task_description": """## CURRENT TASK: Look at all the available data and take some time to analyze it. Look at the job description and the work profile of the user, and consider what areas should be focused, reinforced, and even removed to ensure they have the best chance to get an interview. DO NOT WRITE THE CV YET, just brainstorm ideas.""",
#     }
# )
# cv_cover_letter_task = CVGenerationTask(
#     task_name="cv_cover_letter_task",
#     task_description="Generate a cover letter based on the user's history and the job description.",
#     input_variables=cv_cover_letter_parameters,
#     prompts_to_add={
#         "task_description": """## CURRENT TASK: Based on the job description and the user's history, write a cover letter that highlights the user's strengths and experiences. Remember to make it tailored to the job description and user's history.""",
#     }
# )
# cv_cv_generation_task = CVGenerationTask(
#     task_name="cv_cv_generation_task",
#     task_description="Generate a CV based on the user's history and the job description.",
#     input_variables=cv_cv_generation_parameters,
#     prompts_to_add={
#         "task_description": """## CURRENT TASK: Based on all the information available, write a CV that highlights the user's strengths and experiences. Remember to make it tailored to the job description and user's history.""",
#     }
# )
# cv_generation_workflow = Workflow(
#     task_name="cv_generation_workflow",
#     task_description="Generate a CV and cover letter based on the job description and user history.",
#     input_variables=cv_clarifications_parameters,
#     tasks={
#         "cv_clarifications_task": cv_clarifications_task,
#         "user_clarifications_task": user_clarifications_task,
#         "cv_brainstorming_task": cv_brainstorming_task,
#         "cv_cover_letter_task": cv_cover_letter_task,
#         "cv_cv_generation_task": cv_cv_generation_task,
#     },
#     start_task="cv_clarifications_task",
#     tasks_end_code_routing={
#         "cv_clarifications_task": {
#             0: ("user_clarifications_task", False),
#             1: ("cv_generation_task", True),
#         },
#         "user_clarifications_task": {
#             0: ("cv_brainstorming_task", False),
#             1: ("cv_brainstorming_task", False),
#         },
#         "cv_brainstorming_task": {
#             0: ("cv_cover_letter_task", False),
#             1: ("cv_brainstorming_task", False),
#         },
#         "cv_cover_letter_task": {
#             0: ("cv_cv_generation_task", True),
#             1: ("cv_cover_letter_task", False),
#         },
#         "cv_cv_generation_task": {
#             0: (None, True),
#             1: ("cv_cv_generation_task", False),
#         },
#     },
#     max_attempts=3,
#     recursive=False
# )
# code_generation_parameters = FunctionParameters(
#     type="object",
#     properties={
#         "outputs_plan_workflow": ParameterDefinition(
#             type="string",
#             description="The task plan that describes the code requirements for the task",
#             default=None
#         ),
#         "outputs_generate_code": ParameterDefinition(
#             type="string",
#             description="The code that was generated, passed in case of a recursive call",
#             default=None
#         ),
#         "outputs_execute_code": ParameterDefinition(
#             type="string",
#             description="The code execution output that was generated, passed in case of a recursive call",
#             default=None
#         ),
#         "outputs_generate_unit_tests": ParameterDefinition(
#             type="string",
#             description="The unit test code that was generated, passed in case of a recursive call",
#             default=None
#         ),
#         "outputs_execute_unit_tests": ParameterDefinition(
#             type="string",
#             description="The output of the unit test execution, passed in case of a recursive call",
#             default=None
#         )},
#     required=["outputs_plan_workflow"]
# )
code_execution_parameters = FunctionParameters(
    type="object",
    properties={
        "outputs_generate_code": ParameterDefinition(
            type="string",
            description="The code that was generated",
            default=None
        )},    
    required=["outputs_generate_code"]
)
unit_test_generation_parameters = FunctionParameters(
    type="object",
    properties={
        "outputs_plan_workflow": ParameterDefinition(
            type="string",
            description="The task plan that describes the code requirements for the task",
            default=None
        ),
        "outputs_generate_code": ParameterDefinition(
            type="string",
            description="The code that was generated",
            default=None
        ),
        "outputs_execute_code": ParameterDefinition(
            type="string",
            description="The code execution output that was generated",
            default=None
        ),
        "outputs_generate_unit_tests": ParameterDefinition(
            type="string",
            description="The unit test code that was generated, passed in case of a recursive call",
            default=None
        ),
        "outputs_execute_unit_tests": ParameterDefinition(
            type="string",
            description="The output of the unit test execution, passed in case of a recursive call",
            default=None
        )},
    required=["outputs_plan_workflow", "outputs_generate_code", "outputs_execute_code"]
)
unit_test_execution_parameters = FunctionParameters(
    type="object",
    properties={
        "outputs_generate_code": ParameterDefinition(
            type="string",
            description="The code that was generated",
            default=None
        ),
        "outputs_generate_unit_tests": ParameterDefinition(
            type="string",
            description="The unit test code that was generated",
            default=None
        )},
    required=["outputs_generate_code", "outputs_generate_unit_tests"]
)
unit_test_execution_check_parameters = FunctionParameters(
    type="object",
    properties={
        "outputs_generate_code": ParameterDefinition(
            type="string",
            description="The code that was generated",
            default=None
        ),
        "outputs_generate_unit_tests": ParameterDefinition(
            type="string",
            description="The unit test code that was generated",
            default=None
        ),
        "outputs_execute_unit_tests": ParameterDefinition(
            type="string",
            description="The output of the unit test execution",
            default=None
        )},
    required=["outputs_generate_code", "outputs_generate_unit_tests", "outputs_execute_unit_tests"]
)
# plan_workflow = PromptAgentTask(
#     task_name="plan_workflow",
#     task_description="Takes a simple prompt and develops it into a full task prompt",
#     agent_name="coding_planner_agent",
# )
# generate_code = CodeGenerationLLMTask(
#     task_description="Generates code based on the provided plan_workflow output",
#     input_variables=code_generation_parameters,
#     templates={"task_template": "code_generation_task"}
# )
# execute_code = CodeExecutionLLMTask(
#     task_description="Executes the code available in a list of message dicts",
#     input_variables=code_execution_parameters,
#     templates={"task_template": "code_execution_task"}
# )
# generate_unit_tests = CodeGenerationLLMTask(
#     task_name="generate_unit_tests",
#     task_description="Generates unit tests for the prompt provided. Ensure the code and task are available in the prompt",
#     agent_name="unit_tester_agent",
#     input_variables=unit_test_generation_parameters,
#     templates={"task_template": "unit_test_generation_task"}
# )
# execute_unit_tests = CodeExecutionLLMTask(
#     task_name="execute_unit_tests",
#     task_description="Executes the code available in a list of message dicts",
#     agent_name="executor_agent",
#     input_variables=unit_test_execution_parameters,
#     templates={"task_template": "unit_test_execution_task"}
# )
# check_unit_test_results = CheckTask(
#     agent_name="unit_test_execution_checker_agent",
#     task_name="check_unit_test_results",
#     task_description="Checks the results of the unit tests",
#     input_variables=unit_test_execution_check_parameters,
#     exit_code_response_map={"FAILED": 2, "TEST PASSED": 0, "TEST CODE ERROR": 3},
#     exit_codes={0: "Test Passed", 1: "Response generation failed", 2: "Test Failed"},
#     templates={"task_template": "unit_test_execution_check_task"}
# )
# coding_workflow = Workflow(
#     task_name="coding_workflow",
#     task_description="Executes a coding workflow based on the provided prompt",
#     tasks={
#         "plan_workflow": plan_workflow,
#         "generate_code": generate_code,
#         "execute_code": execute_code,
#         "generate_unit_tests": generate_unit_tests,
#         "execute_unit_tests": execute_unit_tests,
#         "check_unit_test_results": check_unit_test_results
#     },
#     start_task="plan_workflow",
#     tasks_end_code_routing={
#         "plan_workflow": {
#             0: ("generate_code", False),
#             1: ("plan_workflow", True),
#         },
#         "generate_code": {
#             0: ("execute_code", False),
#             1: ("generate_code", True),
#             2: ("generate_code", True)
#         },
#         "execute_code": {
#             0: ("generate_unit_tests", False),
#             1: ("generate_code", True),
#             2: ("generate_code", True),
#             3: ("execute_code", True)
#         },
#         "generate_unit_tests": {
#             0: ("execute_unit_tests", False),
#             1: ("generate_unit_tests", True),
#             2: ("generate_unit_tests", True)
#         },
#         "execute_unit_tests": {
#             0: ("check_unit_test_results", False),
#             1: ("generate_unit_tests", True),
#             2: ("generate_unit_tests", True),
#             3: ("execute_unit_tests", True)
#         },
#         "check_unit_test_results": {
#             0: (None, False),
#             1: ("check_unit_test_results", True),
#             2: ("generate_code", True),
#             3: ("generate_unit_tests", True)
#         }
#     },
#     max_attempts=5,
#     recursive=False
# )

# search_hub = AgentWithFunctions(
#     task_name="search_hub",
#     task_description="Searches multiple sources and returns the results",
#     agent_name="research_agent",
#     functions={
#         "reddit_search": RedditSearchTask(),
#         "exa_search": ExaSearchTask(),
#         "wikipedia_search": WikipediaSearchTask(),
#         "google_search": GoogleSearchTask(),
#         "arxiv_search": ArxivSearchTask()
#     }
# )

# search_hub = {
#     "task_type": "AgentWithFunctions", 
#     "task_name": "search_hub",
#     "task_description": "Searches multiple sources and returns the results",
#     "agent_name": "research_agent",
#     "functions":[
#         "reddit_search", 
#         "exa_search",
#         "wikipedia_search",
#         "google_search",
#         "arxiv_search"
#     ]
# }
# cv_generation_workflow = {
#     "task_type": "Workflow",
#     "task_name": "cv_generation_workflow",
#     "task_description": "Generate a CV and cover letter based on the job description and user history.",
#     "input_variables": {
#         "type": "object",
#         "properties": {
#             "inputs_job_description": {
#                 "type": "string",
#                 "description": "The job description for which the CV is being created.",
#                 "default": None
#                 },
#             "inputs_user_history": {
#                 "type": "string",
#                 "description": "The user's history and experience.",
#                 "default": None
#                 },
#             "inputs_additional_details": {
#                 "type": "string",
#                 "description": "Additional context or details provided by the user.",
#                 "default": None
#                 },
#             "inputs_request_cover_letter": {
#                 "type": "boolean",
#                 "description": "Whether a cover letter is requested.",
#                 "default": False
#                 },
#         },
#         "required": ["inputs_job_description", "inputs_user_history", "inputs_additional_details", "inputs_request_cover_letter"]
#     },
#     "tasks": {
#         "cv_clarifications_task": "cv_clarifications_task",
#         "user_clarifications_task": "user_clarifications_task",
#         "cv_brainstorming_task": "cv_brainstorming_task",
#         "cv_cover_letter_task": "cv_cover_letter_task",
#         "cv_cv_generation_task": "cv_cv_generation_task",
#     },
#     "start_task": "cv_clarifications_task",
#     "tasks_end_code_routing": {
#         "cv_clarifications_task": {
#             0: ("user_clarifications_task", False),
#             1: ("cv_generation_task", True),
#         },
#         "user_clarifications_task": {
#             0: ("cv_brainstorming_task", False),
#             1: ("cv_brainstorming_task", False),
#         },
#         "cv_brainstorming_task": {
#             0: ("cv_cover_letter_task", False),
#             1: ("cv_brainstorming_task", False),
#         },
#         "cv_cover_letter_task": {
#             0: ("cv_cv_generation_task", True),
#             1: ("cv_cover_letter_task", False),
#         },
#         "cv_cv_generation_task": {
#             0: (None, True),
#             1: ("cv_cv_generation_task", False),
#         },
#     },
#     "max_attempts": 3,
#     "recursive": False
# }

cv_workflow_string_template = """The user has requested the creation of a custom {% if inputs.request_cover_letter %}CV and Cover Letter{% else %}CV{% endif %}. 
Here's the available data for context, but remember to focus on tackling the CURRENT TASK:
# Job description: this is the role the user wants to apply to
{{ inputs_job_description }}
# User's history: this is all the information we have about the user's professional background
{{ inputs_user_history }}
{% if inputs_additional_details %}
# Additional details: provided by the user
{{ inputs_additional_details }}
{% endif %}
{% if outputs %}
{% if outputs_user_clarifications_task and outputs_cv_clarifications_task %}
Based on the provided data we came up with a set of clarifying questions:
{{ outputs_cv_clarifications_task }}
Here is the user input regarding our questions:
{{ outputs_user_clarifications_task }} 
{% endif %}
{% if outputs_cv_brainstorming_task %}
We spent some time brainstorming how to succeed on this task, and these are the recommendations we came up with:
{{ outputs_cv_brainstorming_task }}
{% endif %}
{% if outputs_cover_letter %}
Here is the approved cover letter we prepared:
{{ outputs_cover_letter }}
{% endif %}
{% if outputs_cv_draft %}
Here is the approved CV draft we prepared:
{{ outputs_cv_draft }}
{% endif %}
{% endif %}
{% if task_description %}
## CURRENT TASK: 
{{ task_description }}
{% endif %}"""
# ## Parameters for the CV Generation Workflow
# cv_clarifications_parameters = FunctionParameters(
#     type="object",
#     properties={
#         "inputs_job_description": ParameterDefinition(
#             type="string",
#             description="The job description for which the CV is being created.",
#             default=None
#             ),
#         "inputs_user_history": ParameterDefinition(
#             type="string",
#             description="The user's history and experience.",
#             default=None
#             ),
#         "inputs_additional_details": ParameterDefinition(
#             type="string",
#             description="Additional context or details provided by the user.",
#             default=None
#             ),
#         "inputs_request_cover_letter": ParameterDefinition(
#             type="boolean",
#             description="Whether a cover letter is requested.",
#             default=False
#             ),
#     },
#     required=["inputs_job_description", "inputs_user_history", "inputs_additional_details", "inputs_request_cover_letter"]
# )

# class CVGenerationTask(PromptAgentTask):
#     templates: Dict[str, Prompt] = Field({"task_template": Prompt(is_templated=True, name="cv_workflow_template", content=cv_workflow_string_template, parameters=cv_clarifications_parameters)}, description="A dictionary of template names and their file names. By default this task uses the 'task_template' template to structure the inputs.")
#     agent: AliceAgent = Field(..., description="The agent to use for the task")

available_tasks: List[AliceTask] = [
    # cv_clarifications_task,
    # user_clarifications_task,
    # cv_brainstorming_task,
    # cv_cover_letter_task,
    # cv_cv_generation_task,
    # cv_generation_workflow,
    # plan_workflow,
    # generate_code,
    # execute_code,
    # generate_unit_tests,
    # execute_unit_tests,
    # check_unit_test_results,
    # coding_workflow, 
    RedditSearchTask(), 
    ExaSearchTask(),
    WikipediaSearchTask(),
    GoogleSearchTask(),
    ArxivSearchTask(),
    # search_hub
]
