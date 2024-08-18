import logging
from typing import Dict, Any
from django.db.utils import IntegrityError
from django import forms
from django.core.exceptions import ValidationError
from cms.models import CMSPlugin, Placeholder
from djangocms_plugie.utils import get_importer, ImporterLoadingError, parse_and_validate_import_file, initialize_and_run_importer

logger = logging.getLogger(__name__)

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

        self.validate_plugin_or_placeholder(plugin, placeholder)

        if plugin and not self.is_plugin_bound(plugin):
            raise ValidationError("Plugin is unbound.")
        
        return self.cleaned_data
    
    def validate_plugin_or_placeholder(self, plugin, placeholder):
        """
        Validates that at least one of 'plugin' or 'placeholder' is provided.

        Args:
            plugin: The selected plugin.
            placeholder: The selected placeholder.

        Raises:
            ValidationError: If neither 'plugin' nor 'placeholder' is provided.
        """
        if not any([plugin, placeholder]):
            raise ValidationError("A plugin or placeholder is required.")
        
    def is_plugin_bound(self, plugin) -> bool:
        """
        Checks if the plugin is bound to an existing model.

        Args:
            plugin: The selected plugin.

        Returns:
            bool: True if the plugin is bound, False otherwise.
        """
        plugin_model = plugin.get_plugin_class().model
        return plugin_model.objects.filter(cmsplugin_ptr=plugin).exists()


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
        self.cleaned_data["import_data"] = parse_and_validate_import_file(import_file)

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
        initialize_and_run_importer(data)