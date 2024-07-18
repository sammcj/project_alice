from typing import Dict, Any
from pydantic import BaseModel
import datetime
from workflow_logic.tests.TestModule import TestModule
from workflow_logic.api.db_app import DBStructure

class TestEnvironment(BaseModel):
    modules: Dict[str, TestModule] = {}
    results: Dict[str, Any] = {}

    async def add_module(self, module: TestModule):
        self.modules[module.name] = module

    async def run_module(self, module_name: str, verbose: bool = False, **kwargs) -> Dict[str, Any]:
        if module_name not in self.modules:
            raise ValueError(f"Module {module_name} not found")
        if verbose:
            print(f"\n--- {module_name} Tests ---")
        result = await self.modules[module_name].run(**kwargs)
        result["summary"] = self.parse_results(result["test_results"])
        if verbose:
            self.print_summary(result["summary"], module_name=module_name)
        return result
    
    async def run(self, db_structure: DBStructure, verbose: bool = False, **kwargs) -> Dict[str, Any]:
        self.results["DBTests"] = await self.run_module("DBTests", verbose, db_structure=db_structure)

        if self.modules["APITests"]:
            self.results["APITests"] = await self.run_module("APITests", verbose, db_init_manager=self.results["DBTests"]["outputs"]["db_init_manager"])

        if self.modules["ChatTests"]:
            self.results["ChatTests"] = await self.run_module("ChatTests", verbose, db_init_manager=self.results["DBTests"]["outputs"]["db_init_manager"])

        return self.results
    
    @staticmethod
    def print_summary(summary: Dict[str, Any], module_name: str):
        print("\n--- Test Summary ---")
        print(f'Module: {module_name}')
        print(f"Status: {summary['status'].upper()}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['success_count']}")
        print(f"Errors: {summary['error_count']}")
        print(f"Failures: {summary['failure_count']}")

        if summary['errors']:
            print("\nErrors:")
            for error in summary['errors']:
                print(f"  - {error}")

        if summary['failures']:
            print("\nFailures:")
            for failure in summary['failures']:
                print(f"  - {failure}")

    @staticmethod
    def parse_results(results: Dict[str, Any]) -> Dict[str, Any]:
        status = 'success'
        error_count = 0
        failure_count = 0
        success_count = 0
        errors = []
        failures = []

        for key, value in results.items():
            if key == 'initialization':
                if value != 'Success':
                    status = 'failed'
                    failure_count += 1
                    failures.append(f"Initialization failed: {value}")
            elif value == 'Success':
                success_count += 1
            elif 'error' in value.lower():
                status = 'with_errors' if status != 'failed' else status
                error_count += 1
                errors.append(f"{key}: {value}")
            else:
                status = 'with_errors' if status != 'failed' else status
                failure_count += 1
                failures.append(f"{key}: {value}")

        total_tests = success_count + error_count + failure_count

        return {
            'status': status,
            'total_tests': total_tests,
            'success_count': success_count,
            'error_count': error_count,
            'failure_count': failure_count,
            'errors': errors,
            'failures': failures,
            'timestamp': datetime.datetime.now().isoformat()
        }