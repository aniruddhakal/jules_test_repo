# Generative Chatbot with API Integration and Policy Adherence

This project implements a generative chatbot that uses a Large Language Model (LLM) via Langchain to formulate responses, adhere to company policies, and integrate with specific API endpoints.

## Features

-   Integrates with Langchain for flexible LLM interaction.
-   Configurable LLM provider (OpenAI, Google Gemini supported; local as a placeholder) via `config.yaml`.
-   Connects to simulated APIs to fetch relevant information or execute actions (`OrderTracking`, `OrderCancellation`).
-   Handles order cancellation requests according to a defined policy (cancellation within 10 days).
-   Provides order tracking information.
-   Basic command-line interface for interaction.
-   Enhanced conversational abilities for general order inquiries.
-   Topic redirection to keep conversations focused on order management.

## Project Structure

-   `config.yaml`: Configuration file for LLM provider, model settings, and API keys.
-   `requirements.txt`: Lists Python dependencies.
-   `chatbot/`: Contains the core chatbot logic.
    -   `main.py`: Entry point for the chatbot application.
    -   `llm_integration.py`: Handles intent recognition and entity extraction using the configured LLM via Langchain.
    -   `llm_manager.py`: Manages the initialization of LLM instances based on `config.yaml`.
    -   `config_loader.py`: Loads and parses `config.yaml`.
    -   `api_client.py`: Manages calls to simulated API endpoints.
    -   `policy_engine.py`: Enforces company policies (e.g., order cancellation).
-   `apis/`: Contains the simulated API implementations.
    -   `order_management.py`: Simulates order cancellation and tracking functionalities.
-   `experiments/`: Contains files related to testing and evaluation.
    -   `test_cases.md`: Describes various scenarios to test the chatbot.
    -   `evaluator.py`: (Placeholder) Scripts for evaluating chatbot performance.
-   `README.md`: This file.

## Setup and Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the LLM Provider (`config.yaml`):**
    -   Open `config.yaml` in the root directory.
    -   Set the `provider` you wish to use (e.g., "openai", "google_gemini").
    -   Review the settings for your chosen provider (e.g., `openai_settings`, `google_gemini_settings`).
        -   You can change the `model` if needed.
        -   Ensure the `api_key_env_var` points to the correct environment variable name where your API key will be stored.

5.  **Set API Keys (Crucial for Cloud LLMs):**
    -   For cloud-based LLMs like OpenAI or Google Gemini, you **must** set the API key as an environment variable.
    -   For example, if `config.yaml` has:
        ```yaml
        openai_settings:
          api_key_env_var: "OPENAI_API_KEY"
        ```
        You need to set the `OPENAI_API_KEY` environment variable in your system:
        ```bash
        export OPENAI_API_KEY="your_actual_openai_api_key" # Linux/macOS
        # set OPENAI_API_KEY=your_actual_openai_api_key    # Windows (cmd)
        # $env:OPENAI_API_KEY="your_actual_openai_api_key" # Windows (PowerShell)
        ```
    -   Replace `"your_actual_openai_api_key"` with your real API key. Do the same for other providers if you switch.
    -   **Without the correct API key environment variable set, the chatbot will not be able to use cloud-based LLMs and will report an error on startup.**

## Running the Chatbot

Once the setup is complete and API keys are configured (if using cloud LLMs):

## Evaluation
- The `experiments/evaluation_metrics.md` file details a comprehensive set of quantitative and
  qualitative metrics for assessing chatbot performance and decision-making.
- Test cases can be found in `experiments/test_cases.md`.

```bash
python chatbot/main.py
```

This will start the chatbot in your terminal. Follow the on-screen prompts to interact with it.

## TODO (Post LLM Integration)

-   Implement robust support for local LLMs (e.g., GGUF models via LlamaCpp).
-   Explore Langgraph for more complex conversational flows and agentic behavior.
-   Develop more sophisticated dialogue management (e.g., handling context over multiple turns).
-   Enhance error handling and user feedback.
-   Build out the `experiments/evaluator.py` for more systematic testing.
-   Add more policies and API integrations.
