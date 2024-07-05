import logging
from django.db.utils import IntegrityError
import json
from django import forms
from django.core.exceptions import ValidationError
from cms.models import CMSPlugin, Placeholder
import importlib

logger = logging.getLogger(__name__)


def _get_parsed_data(file_obj):
    raw = file_obj.read().decode("utf-8")
    return json.loads(raw)


def _get_importer(version):
    try:
        major_version = version.split(".")[0]
        module_name = f"djangocms_plugie.version{major_version}.importer"
        class_name = "Importer"
        module = importlib.import_module(module_name)
        importer = getattr(module, class_name)()
        return importer

    except ImportError as e:
        logger.error(f"Error importing module: {e}")
        raise ImportError(
            f"It was not possible to import the importer for version {str(version)}. Check if the version exists or if \
            the module is correctly implemented.")
    except AttributeError as e:
        logger.error(f"Error importing class: {e}")
        raise AttributeError(
            f"File version must be in the format 'x.y.z', where x is the major version. Got: {str(version)}")


class PluginImporterForm(forms.Form):
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

    def clean(self):
        if self.errors:
            return self.cleaned_data

        plugin = self.cleaned_data.get("plugin")
        placeholder = self.cleaned_data.get("placeholder")

        if not any([plugin, placeholder]):
            message = "A plugin or placeholder is required."
            raise forms.ValidationError(message)

        if plugin:
            plugin_model = plugin.get_plugin_class().model
            plugin_is_bound = plugin_model.objects.filter(cmsplugin_ptr=plugin).exists()
        else:
            plugin_is_bound = False

        if plugin and not plugin_is_bound:
            raise ValidationError("Plugin is unbound.")
        return self.cleaned_data


class ImportForm(PluginImporterForm):
    import_file = forms.FileField(required=True)

    def clean(self):
        if self.errors:
            return self.cleaned_data

        import_file = self.cleaned_data["import_file"]

        try:
            data = _get_parsed_data(import_file)
            if not isinstance(data, dict) or "version" not in data or "all_plugins" not in data:
                raise ValidationError(
                    "File is not valid: the Import file must be a dictionary with keys 'version' and 'all_plugins'")

            version = data.get("version")
            # TODO: refactor this validation
            if not version or not isinstance(version, str) or len(version.split(".")) != 3:
                raise ValidationError("File is not valid: 'version' is not a string with format 'x.y.z'")

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
                    raise ValidationError(
                        "File is not valid: a plugin is missing required keys in 'meta': %(keys)s",
                        code='missing_keys', params={"keys": missing_keys})

        except (ValueError, TypeError, AttributeError) as e:
            raise ValidationError(f"File is not valid. Error: {e}")

        self.cleaned_data["import_data"] = data
        return self.cleaned_data

    def run_import(self):
        data = self.cleaned_data
        target_plugin = data["plugin"]

        if target_plugin:
            data["placeholder"] = target_plugin.placeholder

        version = data["import_data"]["version"]
        importer = _get_importer(version)

        try:
            importer.import_plugins_to_target(data)
        # TODO: refactor these errors
        except (TypeError, IntegrityError, ValueError) as e:
            raise TypeError(f"Error importing plugin tree: {e}")
        except Exception as e:
            raise Exception(f"Error importing plugin tree: {e}")
