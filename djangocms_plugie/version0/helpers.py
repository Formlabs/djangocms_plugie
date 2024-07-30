import logging
from cms.api import add_plugin, _verify_plugin_type
from django.db.utils import IntegrityError
from django.db import transaction
from cms.plugin_pool import plugin_pool
from djangocms_plugie.version0.utils import handle_special_plugin_fields

logger = logging.getLogger(__name__)


class PluginContext:
    def __init__(self, placeholder, plugin_fields, target_plugin=None):
        self.placeholder = placeholder
        self.plugin_fields = plugin_fields
        self.target_plugin = target_plugin

    @property
    def plugin_model(self):
        try:
            plugin_model, _ = _verify_plugin_type(self.plugin_type)
            return plugin_model
        except Exception as e:
            logger.exception(e)
            raise TypeError(
                f"A plugin doesn't exist. Plugin: {self.plugin_type}")

    @property
    def plugin_type(self):
        return self.meta.get("plugin_type")

    def set_plugin_type(self, plugin_type):
        self.meta['plugin_type'] = plugin_type

    @property
    def meta(self):
        return self.plugin_fields.get("meta")

    @property
    def non_meta_fields(self):
        return {key: value for key, value in self.plugin_fields.items() if key != "meta"}

    @property
    def parent_id(self):
        return self.meta.get("parent")

    @property
    def position(self):
        return self.meta.get("position")

    @property
    def source_id(self):
        return self.meta.get("id")

    def increment_position_by(self, increment):
        self.meta["position"] += increment

    def validate_root_plugin(self):
        parent_plugin = self.target_plugin
        child_type = self.plugin_type
        if not self._is_valid_child(parent_plugin, child_type):
            raise TypeError(
                f"Plugin type {child_type} is not allowed as a child of {getattr(parent_plugin, 'plugin_type', None)}")
        if not self._is_valid_parent(parent_plugin, child_type):
            raise TypeError(
                f"Plugin {child_type} requires a parent of type {self._get_allowed_parents(child_type)}")

    def _is_valid_child(self, parent_plugin, child_type):
        allowed_children = self._get_allowed_children(parent_plugin)
        return allowed_children is None or child_type in allowed_children

    def _is_valid_parent(self, parent_plugin, child_type):
        allowed_parents = self._get_allowed_parents(child_type)
        return allowed_parents is None or getattr(parent_plugin, 'plugin_type', None) in allowed_parents

    @staticmethod
    def _get_allowed_children(plugin):
        if plugin is None:
            return None

        plugin_class = getattr(plugin, 'get_plugin_class', lambda: None)()
        if not plugin_class:
            raise TypeError(f"Can't retrieve plugin class for plugin {plugin}")

        allow_children = getattr(plugin_class, 'allow_children', False)

        return plugin_class.child_classes if allow_children else []

    @staticmethod
    def _get_allowed_parents(plugin_type: str):
        try:
            plugin_class = plugin_pool.get_plugin(plugin_type)
            return plugin_class().parent_classes
        except KeyError:
            raise TypeError(f"A plugin doesn't exist. Plugin: {plugin_type}")

    def create_dummy_plugin(self):
        self.set_plugin_type('WrapperPlugin')
        return self._add_plugin()

    def create_plugin(self, method_map):
        non_meta_fields = self.non_meta_fields
        plugin_model = self.plugin_model
        initial_fields = self._get_initial_fields(
            non_meta_fields, plugin_model)
        processed_initial_fields = handle_special_plugin_fields(
            initial_fields, None, method_map)

        with transaction.atomic():
            new_plugin = self._add_plugin(**processed_initial_fields)

            remaining_fields = {
                key: value for key, value in non_meta_fields.items() if key not in initial_fields}
            if remaining_fields:
                new_plugin = self._update_new_plugin(
                    new_plugin, remaining_fields, method_map)

            return new_plugin

    def _add_plugin(self, **kwargs):
        placeholder = self.placeholder
        target = self.target_plugin
        plugin_type = self.meta.get("plugin_type")
        language = self.meta.get("language", 'en')
        try:
            return add_plugin(placeholder, plugin_type, language, target=target, **kwargs)
        except TypeError as e:
            logger.exception(e)
            raise TypeError(
                f"A plugin can't be imported. Plugin: {plugin_type}")
        except IntegrityError as e:
            logger.exception(e)
            raise IntegrityError(f"Plugin data is not valid or is missing required fields. Plugin: \
                                {plugin_type}. Error: {e}")

    @staticmethod
    def _get_initial_fields(plugin_fields, plugin_model):
        initial_fields = {}
        model_fields = [field.name for field in plugin_model._meta.fields]
        all_plugin_fields = plugin_fields.items()
        for key, value in all_plugin_fields:
            # TODO: extract this logic to a separate method
            if isinstance(value, dict) and value.get('_type') == 'inline':
                continue
            # TODO: extract this logic to a separate method
            if key not in model_fields:
                continue
            initial_fields[key] = value
        return initial_fields

    def _update_new_plugin(self, instance, fields, method_map):
        deserialized_fields = handle_special_plugin_fields(
            fields, instance.id, method_map)
        updated_instance = self._update_plugin_fields(
            instance, deserialized_fields)
        return updated_instance

    def _update_plugin_fields(self, instance, fields):
        for field_name, value in fields.items():
            setattr(instance, field_name, value)
        instance.save()
        return instance
