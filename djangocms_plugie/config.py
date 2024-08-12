
import json
import logging

logger = logging.getLogger(__name__)

class InvalidConfigError(Exception):
    """Raised when the configuration file is invalid."""

    def __init__(self, message):
        super().__init__(message)

class Config:
    def __init__(self):
        self.dummy_plugins = []
        self.skip_fields = []
        self.config_file = "plugie_config.json"
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
            
            self.dummy_plugins = self.config.get("dummy_plugins", [])
            self.skip_fields = self.config.get("skip_fields", [])
        
        except FileNotFoundError:
            raise InvalidConfigError(f"Configuration file '{self.config_file}' not found. Run 'plugie <project_dir>' to set up the project.")
        
        except json.JSONDecodeError:
           logger.warning(f"Configuration file '{self.config_file}' contains invalid JSON. Using default settings.")
           pass

    def get_dummy_plugins(self):
        return self.dummy_plugins

    def get_skip_fields(self):
        return self.skip_fields