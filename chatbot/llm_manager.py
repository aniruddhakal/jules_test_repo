import sys # Moved import sys to the top
import os

# Adjust sys.path to allow direct execution and importing from 'chatbot' package
# This ensures that 'from chatbot.config_loader import load_config' works when running the script directly.
current_script_path = os.path.abspath(__file__)
chatbot_dir = os.path.dirname(current_script_path)
project_root = os.path.dirname(chatbot_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
# Placeholder for other potential LLMs, e.g., from langchain_community
# from langchain_community.llms import LlamaCpp

from chatbot.config_loader import load_config

def get_llm():
    """
    Factory function to create and return a Langchain LLM instance based on
    the settings in config.yaml.

    It loads the configuration, checks the specified provider, and initializes
    the corresponding LLM. Handles API key retrieval from environment variables.

    Returns:
        A Langchain LLM instance (e.g., ChatOpenAI, ChatGoogleGenerativeAI) or None
        if configuration is missing, API key is not set, or provider is unsupported.
    """
    config = load_config()
    if not config:
        print("Error: LLM Manager - Configuration not loaded. Cannot initialize LLM.")
        return None

    provider = config.get("provider")
    llm_instance = None

    if not provider:
        print("Error: LLM Manager - 'provider' not specified in config.yaml.")
        return None

    print(f"LLM Manager: Attempting to initialize LLM for provider: {provider}")

    try:
        if provider == "openai":
            settings = config.get("openai_settings")
            if not settings:
                print("Error: LLM Manager - 'openai_settings' not found in config for OpenAI provider.")
                return None

            api_key_env_var = settings.get("api_key_env_var")
            model_name = settings.get("model", "gpt-3.5-turbo") # Default model if not specified

            if not api_key_env_var:
                print("Error: LLM Manager - 'api_key_env_var' not specified in openai_settings.")
                return None

            api_key = os.getenv(api_key_env_var)
            if not api_key:
                print(f"Error: LLM Manager - Environment variable '{api_key_env_var}' for OpenAI API key is not set.")
                print("Please set this environment variable to use the OpenAI provider.")
                return None

            llm_instance = ChatOpenAI(api_key=api_key, model_name=model_name)
            print(f"LLM Manager: Successfully initialized ChatOpenAI with model '{model_name}'.")

        elif provider == "google_gemini":
            settings = config.get("google_gemini_settings")
            if not settings:
                print("Error: LLM Manager - 'google_gemini_settings' not found in config for Google Gemini provider.")
                return None

            api_key_env_var = settings.get("api_key_env_var")
            model_name = settings.get("model", "gemini-pro") # Default model

            if not api_key_env_var:
                print("Error: LLM Manager - 'api_key_env_var' not specified in google_gemini_settings.")
                return None

            api_key = os.getenv(api_key_env_var)
            if not api_key:
                print(f"Error: LLM Manager - Environment variable '{api_key_env_var}' for Google API key is not set.")
                print("Please set this environment variable to use the Google Gemini provider.")
                return None

            # Note: For ChatGoogleGenerativeAI, the API key is often set via GOOGLE_API_KEY env var by default,
            # but langchain allows explicit passing. Here we use the one from config.
            llm_instance = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
            print(f"LLM Manager: Successfully initialized ChatGoogleGenerativeAI with model '{model_name}'.")

        elif provider == "local":
            settings = config.get("local_settings")
            print(f"LLM Manager: 'local' provider selected. Settings: {settings}")
            print("Warning: LLM Manager - Local model support is not fully implemented yet. Returning None.")
            # Example for future LlamaCpp integration (would require langchain_community):
            # if settings and settings.get("model_path"):
            #     llm_instance = LlamaCpp(model_path=settings["model_path"], n_gpu_layers=1, n_batch=512, verbose=True)
            #     print(f"LLM Manager: Attempted to initialize local model from {settings['model_path']}.")
            # else:
            #     print("Error: LLM Manager - 'model_path' not specified in local_settings.")
            return None # Or raise NotImplementedError("Local LLM support not yet implemented")

        else:
            print(f"Error: LLM Manager - Unsupported LLM provider '{provider}' specified in config.yaml.")
            print("Supported providers are: 'openai', 'google_gemini', 'local'.")
            return None

    except Exception as e:
        print(f"Error: LLM Manager - An unexpected error occurred while initializing LLM for provider '{provider}': {e}")
        # This could be due to incorrect API keys (though we check for presence), network issues,
        # or other issues with the LLM provider's SDK.
        return None

    return llm_instance

if __name__ == '__main__':
    # Note: sys.path modification is now at the top of the file.
    print("--- Testing LLM Manager ---")

    # To test this, you would need to:
    # 1. Have a valid config.yaml in the parent directory.
    # 2. Set the corresponding API key environment variable (e.g., OPENAI_API_KEY or GOOGLE_API_KEY)
    #    if your config.yaml is set to 'openai' or 'google_gemini'.

    # Example: Temporarily set an environment variable for testing if you haven't set it globally
    # os.environ["OPENAI_API_KEY"] = "your_actual_openai_api_key_if_testing_live"
    # os.environ["GOOGLE_API_KEY"] = "your_actual_google_api_key_if_testing_live"

    print("Attempting to get LLM instance based on config.yaml...")
    llm = get_llm()

    if llm:
        print("\nLLM Instance obtained successfully:")
        print(type(llm))

        # You could try a simple invocation if the LLM is not None
        # This requires the LLM to be properly configured and API key valid.
        # Be cautious with actual API calls during simple tests.
        # print("\nAttempting a simple test invocation (will make an API call if not local)...")
        # try:
        #     # from langchain_core.messages import HumanMessage
        #     # response = llm.invoke([HumanMessage(content="Hello, what is your name?")])
        #     # print(f"Test LLM Response: {response.content}")
        #     print("Test invocation skipped in this example to avoid unintended API calls.")
        #     print("Uncomment and provide API keys to test live invocation.")
        # except Exception as e:
        #     print(f"Error during test invocation: {e}")
    else:
        print("\nFailed to obtain LLM instance. Check configuration and API key environment variables.")

    # To test other providers, you would change 'provider' in config.yaml
    # and ensure the relevant settings and API keys (if applicable) are correct.
    # For example, to test 'local' (which is currently a placeholder):
    # Change provider to "local" in config.yaml, then run this script.
    # You should see the "Local model support is not fully implemented yet" message.
