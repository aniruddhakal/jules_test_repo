# jules_test_repo
zd challenge jules test repo

# Generative Chatbot with API Integration and Policy Adherence

This project implements a generative chatbot that uses an LLM to formulate responses while adhering to company policies and integrating with specific API endpoints.

## Project Structure

-   `chatbot/`: Contains the core chatbot logic.
    -   `main.py`: Entry point for the chatbot application.
    -   `llm_integration.py`: Handles interaction with the (simulated) LLM.
    -   `api_client.py`: Manages calls to simulated API endpoints.
    -   `policy_engine.py`: Enforces company policies.
-   `apis/`: Contains the simulated API implementations.
    -   `order_management.py`: Simulates order cancellation and tracking functionalities.
-   `experiments/`: Contains files related to testing and evaluation.
    -   `test_cases.md`: Describes various scenarios to test the chatbot.
    -   `evaluator.py`: (Placeholder) Scripts for evaluating chatbot performance.
-   `README.md`: This file, providing an overview of the project.

## Features

-   Connects to APIs to fetch relevant information or execute actions.
-   Handles order cancellation requests according to defined policies.
-   Provides order tracking information.

## TODO

-   Implement simulated LLM interaction.
-   Define and implement API endpoint simulations.
-   Develop the policy engine logic.
-   Build the main chatbot orchestration logic.
-   Design and document detailed test cases.
-   Develop evaluation metrics and reporting.
