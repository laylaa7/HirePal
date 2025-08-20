# file: config_manager.py
import json
import os



class ConfigManager:
    _instance = None

    def __new__(cls, config_file_path="config.json"):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config(config_file_path)
        return cls._instance

    def _load_config(self, file_path):
        try:
            # Use os.path.abspath to handle relative paths gracefully
            absolute_path = os.path.abspath(file_path)
            with open(absolute_path, 'r') as f:
                config_data = json.load(f)
                self.PROJECT_ID = config_data.get("PROJECT_ID")
                self.REGION = config_data.get("REGION")
                self.BUCKET_URI = config_data.get("BUCKET_URI")
                self.DIMENSIONS = config_data.get("DIMENSIONS")
                # Set other attributes dynamically if needed
                for key, value in config_data.items():
                    setattr(self, key, value)

        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {file_path}")