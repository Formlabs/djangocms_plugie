import json
import importlib
from types import ModuleType
from typing import Dict, IO, Any, Type
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

REQUIRED_META_KEYS = {"parent", "id", "position", "plugin_type", "depth"}

class ImporterLoadingError(Exception):
    """Error raised when the importer module cannot be loaded."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)



def extract_major_version(version: str) -> str:
    """
    Extract the major version from the version string.
    Example: "0.1.2" -> "0"

    :param version: str, the version string in the format "x.y.z", where x is
    the major version
    """
    try:
        major_version = version.split(".")[0]
        if not major_version.isdigit():
            raise ValueError(f"Major version is not a digit: {major_version}")
        return major_version
    except (AttributeError, IndexError) as e:
        raise ValueError(f"Error extracting major version from {version}: {e}")
    
def get_module_name(major_version: str) -> str:
    """
    Get the module name based on the major version.
    
    :param major_version: str, the major version of the importer
    
    :return: str, the module name
    """
    if not isinstance(major_version, str):
        raise TypeError(f"Major version must be a string: {major_version}")
    if not major_version:
        raise ValueError("Major version cannot be empty")
    if not major_version.isdigit():
        raise ValueError(f"Major version must be a digit: {major_version}")
    return f"djangocms_plugie.importer.version{major_version}.importer"

def import_module(module_name: str) -> ModuleType:
    """
    Import the module based on the module name.
    
    :param module_name: str, the name of the module to import
    
    :return: ModuleType object
    """
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        raise ImportError(f"Error importing module {module_name}: {e}")
    
def get_importer_class(module: ModuleType) -> Type[Any]:
    # TODO: In order to type annotate this function, we need to create a base
    # class for the Importer and have all versions of the importer inherit from
    # it. This way, we can type hint the return type of this function as the base
    # class.
    """
    Get the Importer class from the module.
    
    :param module: ModuleType object
    
    :return: Importer class
    """
    try:
        return getattr(module, "Importer")
    except Exception as e:
        raise AttributeError(f"Error getting Importer class from module {module.__name__}: {e}")
    
def get_importer(data: Dict[str, Any]) -> object:
    # TODO: In order to type annotate this function, we need to create a base
    # class for the Importer and have all versions of the importer inherit from
    # it. This way, we can type hint the return type of this function as the base
    # class.
    """
    Get the importer class based on the version of the import file.

    :param data: dict, the parsed data from the import file

    :return: Importer object
    """
    try:
        version = data["import_data"]["version"]
        major_version = extract_major_version(version)
        module_name = get_module_name(major_version)
        module = import_module(module_name)
        importer = get_importer_class(module)

        return importer(data=data)
    except Exception as e:
        raise ImporterLoadingError(f"Error loading importer: {e}")
    
def parse_import_file(import_file: IO[bytes]) -> Dict[str, Any]:
    """
    Parses the import file and returns the parsed data.

    Args:
        import_file: The import file to be parsed.

    Returns:
        dict: The parsed data.

    Raises:
        ValidationError: If the import file cannot be parsed.
    """
    try:
        raw = import_file.read().decode("utf-8")
        data = json.loads(raw)
        return data
    except Exception as e:
        raise ValidationError(f"File is not valid: {e}")
    
def validate_parsed_data_structure(data: Dict[str, Any]):
    """
    Validates the structure of the parsed data.

    Args:
        data: The parsed data.

    Raises:
        ValidationError: If the data structure is invalid.
    """
    if not isinstance(data, dict) or "version" not in data or "all_plugins" not in data:
        raise ValidationError(
            "File is not valid: the Import file must be a dictionary "
            "with keys 'version' and 'all_plugins'")
    
def validate_version(version: str):
    """
    Validates the version format.

    Args:
        version: The version string.

    Raises:
        ValidationError: If the version format is invalid.
    """
    if not version or not isinstance(version, str) or len(version.split(".")) != 3:
        raise ValidationError(
            "File is not valid: 'version' is not a string with format 'x.y.z'")
    
def validate_all_plugins(all_plugins: list):
    """
    Validates the 'all_plugins' list.

    Args:
        all_plugins: The list of all plugins.

    Raises:
        ValidationError: If the 'all_plugins' list is invalid.
    """
    if not all_plugins or not isinstance(all_plugins, list):
        raise ValidationError("File is not valid: missing 'all_plugins'")

    for plugin in all_plugins:
        validate_plugin_meta(plugin, REQUIRED_META_KEYS)

def validate_plugin_meta(plugin: Dict[str, Any], required_meta_keys: set):
    """
    Validates the 'meta' keys in each plugin.

    Args:
        plugin: The plugin data.
        required_meta_keys: The set of required meta keys.

    Raises:
        ValidationError: If the 'meta' keys are invalid.
    """
    if "meta" not in plugin:
        raise ValidationError("File is not valid: a plugin is missing 'meta' key")

    meta = plugin.get("meta")
    if not isinstance(meta, dict):
        raise ValidationError("File is not valid: the 'meta' value in a plugin is not a dictionary")

    missing_keys = required_meta_keys - set(meta.keys())
    if missing_keys:
        raise ValidationError("File is not valid: a plugin is missing required keys in 'meta': %(keys)s",
                                params={'keys': ', '.join(missing_keys)})
    
def parse_and_validate_import_file(import_file) -> Dict[str, Any]:
    """
    Parses and validates the import file.

    Args:
        import_file: The import file to be parsed and validated.

    Returns:
        dict: The parsed and validated data.

    Raises:
        ValidationError: If the import file is invalid or contains invalid data.
    """
    data = parse_import_file(import_file)
    validate_parsed_data_structure(data)
    validate_version(data.get("version"))
    validate_all_plugins(data.get("all_plugins"))
    return data

def initialize_and_run_importer(data: Dict[str, Any]) -> None:
    """
    Initializes and runs the importer.

    Args:
        data: The cleaned and validated import data.

    Raises:
        TypeError: If an error occurs during the import process.
        Exception: If an unexpected error occurs.
    """
    target_plugin = data["plugin"]

    if target_plugin:
        data["placeholder"] = target_plugin.placeholder

    try:
        importer = get_importer(data)
        importer.import_plugins_to_target()
    except (ImporterLoadingError, TypeError, IntegrityError, ValueError) as e:
        raise TypeError(f"Error importing plugin tree: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")