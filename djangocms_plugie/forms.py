import json
import logging
import importlib
from typing import Dict, IO, Any, Type
from types import ModuleType
from django.db.utils import IntegrityError
from django import forms
from django.core.exceptions import ValidationError
from cms.models import CMSPlugin, Placeholder

logger = logging.getLogger(__name__)


class ImporterLoadingError(Exception):
    """Error raised when the importer module cannot be loaded."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def _get_parsed_data(file_obj: IO[bytes]) -> Dict[str, Any]:
    """
    Get the parsed data from the import file.
    
    :param file_obj: File object

    :return: dict
    """
    raw = file_obj.read().decode("utf-8")
    return json.loads(raw)


def _get_importer(data: Dict[str, Any]) -> object:
    # TODO: In order to type annotate this function, we need to create a base
    # class for the Importer and have all versions of the importer inherit from
    # it. This way, we can type hint the return type of this function as the base
    # class.
    """
    Get the importer class based on the version of the import file.

    :param data: dict, the parsed data from the import file

    :return: Importer object
    """
    version = data["import_data"]["version"]
    major_version = _extract_major_version(version)
    module_name = _get_module_name(major_version)
    module = _import_module(module_name)
    importer = _get_importer_class(module)

    return importer(data=data)


def _extract_major_version(version: str) -> str:
    """
    Extract the major version from the version string.
    Example: "0.1.2" -> "0"

    :param version: str, the version string in the format "x.y.z", where x is
    the major version
    """
    try:
        return version.split(".")[0]
    except (AttributeError, IndexError) as e:
        msg = f"Error extracting major version from {version}: {e}"
        logger.error(msg)
        raise ImporterLoadingError(msg)


def _get_module_name(major_version):
    """
    Get the module name based on the major version.
    
    :param major_version: str, the major version of the importer
    
    :return: str, the module name
    """
    return f"djangocms_plugie.importer.version{major_version}.importer"


def _import_module(module_name: str) -> ModuleType:
    """
    Import the module based on the module name.
    
    :param module_name: str, the name of the module to import
    
    :return: ModuleType object
    """
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        msg = f"Error importing module {module_name}: {e}"
        logger.error(msg)
        raise ImporterLoadingError(msg)


def _get_importer_class(module: ModuleType) -> Type[Any]:
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
        msg = f"Error getting Importer class from module {module.__name__}: {e}"
        logger.error(msg)
        raise ImporterLoadingError(msg)

    # except FileNotFoundError as e:
    #     logger.error(f"Error importing module: {e}")
    #     raise FileNotFoundError(
    #         "The folder with custom methods does not exist. Make sure to run \
    #             'plugie <project_dir>' first, where <project_dir> is the root \
    #                 directory of your project."
    #     )
    # except ImportError as e:
    #     logger.error(f"Error importing module: {e}")
    #     raise ImportError(
    #         f"It was not possible to import the importer for \
    #             version {str(version)}. Check if the version \
    #             exists or if the module is correctly implemented."
    #     )
    # except AttributeError as e:
    #     logger.error(f"Error importing class: {e}")
    #     raise AttributeError(
    #         f"File version must be in the format 'x.y.z', where x is the \
    #             major version. Got: {str(version)}")


class PluginOrPlaceholderSelectionForm(forms.Form):
    """
    Form for selecting either a specific plugin or a placeholder in which 
    plugins can be imported.

    Attributes:
        plugin (ModelChoiceField): A hidden input field for selecting a plugin.
        placeholder (ModelChoiceField): A hidden input field for selecting a placeholder.
    """
    plugin = forms.ModelChoiceField(
        CMSPlugin.objects.all(),
        required=False,
        widget=forms.HiddenInput(),
    )
    placeholder = forms.ModelChoiceField(
        queryset=Placeholder.objects.all(),
        required=False,
        widget=forms.HiddenInput(),
    )

    def clean(self) -> Dict[str, Any]:
        """
        Cleans and validates the form data, ensuring that at least one of 
        'plugin' or 'placeholder' is provided and that the selected plugin 
        is bound to an existing model.

        Returns:
            dict: The cleaned data if validation is successful.

        Raises:
            ValidationError: If neither 'plugin' nor 'placeholder' is provided 
            or if the plugin is unbound.
        """
        if self.errors:
            return self.cleaned_data

        plugin = self.cleaned_data.get("plugin")
        placeholder = self.cleaned_data.get("placeholder")

        if not any([plugin, placeholder]):
            message = "A plugin or placeholder is required."
            raise forms.ValidationError(message)

        if plugin:
            plugin_model = plugin.get_plugin_class().model
            plugin_is_bound = plugin_model.objects.filter(
                cmsplugin_ptr=plugin).exists()
        else:
            plugin_is_bound = False

        if plugin and not plugin_is_bound:
            raise ValidationError("Plugin is unbound.")
        return self.cleaned_data


class ImportForm(PluginOrPlaceholderSelectionForm):
    """
    Form for importing plugins from a file to a selected plugin or placeholder.

    Inherits from PluginOrPlaceholderSelectionForm to include the selection 
    of a target plugin or placeholder.

    Attributes:
        import_file (FileField): A required file input for uploading the import file.
    """
    import_file = forms.FileField(required=True)

    def clean(self) -> Dict[str, Any]:
        """
        Cleans and validates the import file and ensures it contains valid data 
        for importing plugins. Additionally validates the structure of the 
        import data, checking required fields.

        Returns:
            dict: The cleaned data if validation is successful, including 
            parsed import data.

        Raises:
            ValidationError: If the import file is invalid or contains invalid data.
        """
        if self.errors:
            return self.cleaned_data

        import_file = self.cleaned_data["import_file"]

        try:
            data = _get_parsed_data(import_file)
            if not isinstance(data, dict) or "version" not in data or "all_plugins" not in data:
                raise ValidationError(
                    "File is not valid: the Import file must be a dictionary "
                    "with keys 'version' and 'all_plugins'")

            version = data.get("version")
            # TODO: refactor this validation
            if not version or not isinstance(version, str) or len(version.split(".")) != 3:
                raise ValidationError(
                    "File is not valid: 'version' is not a string with format"
                    "'x.y.z'")

            all_plugins = data.get("all_plugins")
            if not all_plugins or not isinstance(all_plugins, list):
                raise ValidationError("File is not valid: missing 'all_plugins'")

            required_meta_keys = {"parent", "id", "position", "plugin_type", "depth"}
            for plugin in all_plugins:
                if "meta" not in plugin:
                    raise ValidationError("File is not valid: a plugin is missing 'meta' key")

                meta = plugin.get("meta")
                if not isinstance(meta, dict):
                    raise ValidationError("File is not valid: the 'meta' value in a plugin is not a dictionary")

                missing_keys = required_meta_keys - set(meta.keys())

                if missing_keys:
                    raise ValidationError("File is not valid: a plugin is missing required keys in 'meta': %(keys)s",
                        code='missing_keys', params={"keys": missing_keys})

        except (ValueError, TypeError, AttributeError) as e:
            raise ValidationError(f"File is not valid. Error: {e}")

        self.cleaned_data["import_data"] = data
        return self.cleaned_data

    def run_import(self) -> None:
        """
        Executes the import process using the cleaned and validated import data.

        Attempts to import plugins into the target plugin or placeholder. If 
        a target plugin is specified, its associated placeholder is used.

        Raises:
            TypeError: If an error occurs during the import process.
            Exception: If an unexpected error occurs.
        """
        data = self.cleaned_data
        target_plugin = data["plugin"]

        if target_plugin:
            data["placeholder"] = target_plugin.placeholder

        try:
            importer = _get_importer(data)
            importer.import_plugins_to_target()
        except (ImporterLoadingError, TypeError, IntegrityError, ValueError) as e:
            raise TypeError(f"Error importing plugin tree: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
