# Project Alice

## Overview

Project Alice is a sophisticated workflow manager that leverages AI-driven agents to streamline and optimize complex tasks. By integrating various AI models and tools, Project Alice aims to create an intelligent and adaptive system capable of handling a wide range of tasks, from simple automation to intricate problem-solving.

## Scope

The core of Project Alice revolves around the concept of agentic workflows, where specialized agents are orchestrated to execute tasks in a coordinated manner. The project incorporates several key components:

1. **Agentic Workflows**: Task decomposition and execution through specialized agents.
2. **Hubs and Specialists**: Domain-specific hubs (e.g., Search Hub, Coding Hub, Communications Hub) managing specialized tools and agents.
3. **Technical Stack**:
   - **Backend**: Python for task execution, accessible via API.
   - **Database**: MongoDB for storing agents, prompts, tasks, workflows, models, and task results.
   - **Frontend**: React for user interaction with the database and task deployment.
4. **Interface Agents**: Facilitating user interactions through Chat, Task Management, and Configuration Tools.
5. **Integration with Various Tools**: Incorporating APIs and models from Anthropic, OpenAI, and others to enhance functionality.

## Goal

The primary goal of Project Alice is to create a robust and flexible platform that can:
- Automate and optimize workflows across various domains.
- Facilitate seamless communication and task management.
- Adapt and scale with the evolving needs of users.

### Specific Objectives

- **Task Automation**: Enable the creation and execution of complex tasks through a series of coordinated agents.
- **User Interaction**: Develop intuitive interfaces for users to interact with agents and workflows.
- **Scalability**: Ensure the platform can scale to handle increasing complexity and volume of tasks.
- **Integration**: Integrate with a wide range of tools and APIs to enhance functionality and provide comprehensive solutions.

# Status

## Backend
* **Workflows**: Basic workflows operational, including CV creation, search hub, and coding + unit testing.
* **Agents**: Classes for agents, models, templates/prompts, and task results are defined and functional.
* **Database**: MongoDB is deployed and functional, with structures for agents, tasks, workflows, etc.
* **API**: Task execution timeouts addressed, improved task saving/retrieval, and result tracking.
* **Chat**: Added Chat model and routes for enhanced communication capabilities.
* **Data Consistency**: Improved consistency by populating documents and creating virtualizations.

## Frontend
* **Components**: Core components such as HomePage, Header, Chat, Sidebar, and TaskResult are implemented.
* **Integration**: Frontend integrated with backend services for data fetching and task execution.
* **UI Enhancements**: User-friendly UI with icons, tooltips, and consistent navigation.
* **TypeScript Migration**: Transition to TypeScript for type safety and better maintainability.
* **Authentication**: Implemented login logic for secure user access.
* **Workflow Access**: Added functionality to access the workflow endpoint.

## Current Progress
* **Python**: Enhancements to Alice with RAG memory, flexible context structures, and society of mind processes.
* **React Frontend**: Display and interaction with tasks and workflows, chat system for iterative feedback.
* **MongoDB**: User management and privacy controls, adapting database structure to evolving needs.
* **Workflow**: Created BackendAPI class to handle interactions with the backend and initialize libraries.
* **Prompt Management**: Improved Prompt class for better templating and management.

## Pending Tasks
* **Backend**:
   * Further integration and testing of various tools/functions for task execution.
   * Enhancements to Alice's agent logic and interaction capabilities.
   * Refining and expanding chat functionality for seamless agent communication.
* **Frontend**:
   * Completing the Database page with collection selection and item management.
   * Refining user interfaces for better usability and functionality.
   * Developing a comprehensive chat interface for agent, prompt, and task creation.
* **Overall**:
   * Ensuring data serialization for easy tracking/retrieval.
   * Continuous improvements based on user feedback and evolving requirements.
   * Integrating the chat system with agent creation, prompt management, and task execution workflows.

## Short-term Challenges
* Designing and implementing an intuitive chat interface that facilitates easy creation and management of agents, prompts, and tasks.
* Ensuring seamless integration between the chat system and the existing workflow and task execution processes.
* Balancing flexibility and user-friendliness in the agent and task creation process through the chat interface.
* Optimizing the performance and responsiveness of the chat system, especially when handling complex agent interactions and task executions.