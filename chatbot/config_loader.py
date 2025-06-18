import yaml
import os

CONFIG_FILE_NAME = "config.yaml" # Assumes it's in the project root

def get_config_path():
    """
    Determines the absolute path to the config.yaml file.
    Assumes this script is in 'chatbot/' and config.yaml is in the parent directory (project root).
    Adjust if your directory structure is different.
    """
    # Path to the current file (config_loader.py)
    current_file_path = os.path.abspath(__file__)
    # Path to the chatbot directory
    chatbot_dir_path = os.path.dirname(current_file_path)
    # Path to the project root directory (parent of chatbot)
    project_root_path = os.path.dirname(chatbot_dir_path)
    # Path to the config.yaml file
    config_file_path = os.path.join(project_root_path, CONFIG_FILE_NAME)
    return config_file_path

def load_config() -> dict:
    """
    Loads the chatbot configuration from the config.yaml file.

    Returns:
        A dictionary containing the configuration settings.
        Returns an empty dictionary if the file is not found or is invalid.
    """
    config_path = get_config_path()

    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{CONFIG_FILE_NAME}' not found at {config_path}.")
        # In a more robust application, you might raise an exception
        # or have a default configuration.
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        if config_data is None: # Handle empty YAML file
            print(f"Warning: Configuration file '{CONFIG_FILE_NAME}' at {config_path} is empty.")
            return {}
        return config_data
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{CONFIG_FILE_NAME}' at {config_path}: {e}")
        return {}
    except IOError as e:
        print(f"Error reading file '{CONFIG_FILE_NAME}' at {config_path}: {e}")
        return {}

if __name__ == '__main__':
    # Example usage: Load and print the configuration
    print(f"Attempting to load configuration from: {get_config_path()}")
    config = load_config()

    if config:
        print("\n--- Loaded Configuration ---")
        # Pretty print the dictionary
        import json
        print(json.dumps(config, indent=2))

        print("\n--- Accessing Specific Values ---")
        print(f"LLM Provider: {config.get('provider')}")

        openai_settings = config.get('openai_settings', {})
        print(f"OpenAI Model: {openai_settings.get('model')}")
        print(f"OpenAI API Key Env Var: {openai_settings.get('api_key_env_var')}")

        google_settings = config.get('google_gemini_settings', {})
        print(f"Google Gemini Model: {google_settings.get('model')}")
        print(f"Google Gemini API Key Env Var: {google_settings.get('api_key_env_var')}")

        logging_config = config.get('logging', {})
        print(f"Logging Level: {logging_config.get('level')}")

    else:
        print("Configuration could not be loaded.")
