
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

class InvalidConfigError(Exception):
    """Raised when the configuration file is invalid."""

    def __init__(self, message):
        super().__init__(message)

class Config:
    """
    Class to handle the configuration settings for the plugie app.
    
    Attributes:
    - dummy_plugins: dict, including the source and target dummy plugins
    - skip_fields: list, the fields to skip when exporting plugins
    - config_file: str, the name of the configuration file
    - custom_methods_path: str, the path to the custom methods directory. Default is 'plugie/custom_methods'
    """
    def __init__(self):
        self.dummy_plugins = {}
        self.skip_fields = ["placeholder","cmsplugin_ptr", "alias_reference"] # default skip fields
        self.config_file = "plugie_config.json"
        self.custom_methods_path = 'plugie/custom_methods'
        self.load_config()

    def load_config(self) -> None:
        """
        Load the configuration settings from the configuration file.

        Raises:
            InvalidConfigError: If the configuration file is not found or contains invalid JSON.
        """
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
            
            self.dummy_plugins = self.config.get("dummy_plugins", {})
            self.skip_fields += self.config.get("skip_fields", [])
            self.custom_methods_path = self.config.get("custom_methods_path", self.custom_methods_path)
        
        except FileNotFoundError:
            logger.warning(f"Configuration file '{self.config_file}' not found. Using default settings.")
            pass
        
        except json.JSONDecodeError:
           logger.warning(f"Configuration file '{self.config_file}' contains invalid JSON. Using default settings.")
           pass

    def get_dummy_plugins_source(self) -> List[str]:
        """
        Get the source dummy plugins from the configuration settings.

        Returns:
            list: The list of source dummy plugins names.
        """
        if isinstance(self.dummy_plugins, dict):
            return self.dummy_plugins.get("source", [])
        return []
    
    def get_dummy_plugins_target(self) -> str:
        """
        Get the target dummy plugin from the configuration settings.

        Returns:
            str: The target dummy plugin name.
        """
        if isinstance(self.dummy_plugins, dict):
            return self.dummy_plugins.get("target", None)

    def get_skip_fields(self) -> List[str]:
        """
        Get the fields to skip when exporting plugins.

        Returns:
            list: The list of fields to skip.
        """
        return self.skip_fields
    
    def get_custom_methods_path(self) -> str:
        """
        Get the path to the custom methods directory.

        Returns:
            str: The path to the custom methods directory.
        """
        return self.custom_methods_path