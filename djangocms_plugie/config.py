
import json
import logging

logger = logging.getLogger(__name__)

class InvalidConfigError(Exception):
    """Raised when the configuration file is invalid."""

    def __init__(self, message):
        super().__init__(message)

class Config:
    def __init__(self):
        self.dummy_plugins = {}
        self.skip_fields = ["placeholder","cmsplugin_ptr"] # default skip fields
        self.config_file = "plugie_config.json"
        self.custom_methods_path = 'plugie/custom_methods'
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
            
            self.dummy_plugins = self.config.get("dummy_plugins", {})
            self.skip_fields += self.config.get("skip_fields", [])
            self.custom_methods_path = self.config.get("custom_methods_path", self.custom_methods_path)
        
        except FileNotFoundError:
            raise InvalidConfigError(f"Configuration file '{self.config_file}' not found. Run 'plugie <project_dir>' to set up the project.")
        
        except json.JSONDecodeError:
           logger.warning(f"Configuration file '{self.config_file}' contains invalid JSON. Using default settings.")
           pass

    def get_dummy_plugins_source(self):
        if isinstance(self.dummy_plugins, dict):
            return self.dummy_plugins.get("source", [])
        return []
    
    def get_dummy_plugins_target(self):
        if isinstance(self.dummy_plugins, dict):
            return self.dummy_plugins.get("target", None)

    def get_skip_fields(self):
        return self.skip_fields
    
    def get_custom_methods_path(self):
        return self.custom_methods_path