from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from workflow_logic.db_app.db_container import ContainerAPI
from workflow_logic.api_app.middleware.cors import add_cors_middleware
from workflow_logic.api_app.middleware.auth import auth_middleware
from workflow_logic.api_app.routes import health_route, task_execute, chat_response, db_init
from workflow_logic.tests.component_tests.test_environment import TestEnvironment
from workflow_logic.tests.component_tests.db_test import DBTests
from workflow_logic.tests.component_tests.api_test import APITests
from workflow_logic.db_app.initialization_data import DB_STRUCTURE
from workflow_logic.util.logging_config import LOGGER

db_app = None
thread_pool = None

async def run_initial_tests(app: FastAPI):
    test_env = TestEnvironment()
    db_tests = DBTests()
    api_tests = APITests()
    await test_env.add_module(db_tests)
    await test_env.add_module(api_tests)
    test_settings = {
        "db_structure": DB_STRUCTURE,
        "verbose": True
    }
    initial_test_results = await test_env.run(**test_settings)
    app.state.initial_test_results = initial_test_results
    LOGGER.info("Initial tests completed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_app, thread_pool
    db_app = ContainerAPI()
    await db_app.initialize_db_app()
    thread_pool = ThreadPoolExecutor()
    app.state.db_app = db_app
    # Run initial tests
    await run_initial_tests(app)
    yield
    # Clean up resources if necessary
    thread_pool.shutdown()

WORKFLOW_APP = FastAPI(lifespan=lifespan)
add_cors_middleware(WORKFLOW_APP)
WORKFLOW_APP.middleware("http")(auth_middleware)
WORKFLOW_APP.include_router(health_route)
WORKFLOW_APP.include_router(task_execute)
WORKFLOW_APP.include_router(chat_response)
WORKFLOW_APP.include_router(db_init)