import json
from pathlib import Path

# Define the config file path
CONFIG_FILE = Path.home() / ".config" / "yelena-hello" / "config.json"

def load_config():
    """Load configuration settings from file. Return default config if file doesn't exist."""
    default_config = {
        'language': 'en',  # Default language
        'autostart': True,  # Autostart by default
    }
    
    try:
        # Create directory if it doesn't exist
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if config file exists
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Update with any missing default values
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            # Create default config file if it doesn't exist
            save_config(default_config)
            return default_config
    except Exception as e:
        print(f"Error loading config: {e}")
        return default_config

def save_config(config):
    """Save configuration settings to file."""
    try:
        # Create directory if it doesn't exist
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config to file
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # This will load existing config or create a default one if none exists
    config = load_config()
    print(f"Loaded configuration: {config}")
