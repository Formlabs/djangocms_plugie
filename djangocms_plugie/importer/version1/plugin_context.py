import logging
from cms.api import add_plugin, _verify_plugin_type
from django.db import transaction
from cms.plugin_pool import plugin_pool
from djangocms_plugie.importer.version0.utils import handle_special_plugin_fields
from djangocms_plugie.config import Config

logger = logging.getLogger(__name__)
ALL_CHILDREN_ALLOWED = object()
ALL_PARENTS_ALLOWED = object()


class InvalidPluginError(Exception):
    """Raised when an error occurs during plugin import."""

    def __init__(self, message):
        super().__init__(message)


class PluginCreationError(Exception):
    """Raised when an error occurs during plugin creation."""

    def __init__(self, message):
        super().__init__(message)


class PluginContext:
    def __init__(self, plugin_fields, placeholder, plugin_map, root_target_plugin=None):
        self.placeholder = placeholder
        self.plugin_fields = plugin_fields
        self.is_root_plugin = self._is_root_plugin(plugin_map)
        self.target_plugin = self._get_target_plugin(root_target_plugin, plugin_map)
        self.dummy_plugins_target = Config().get_dummy_plugins_target()
        self._validate()

    @property
    def plugin_model(self):
        try:
            plugin_model, _ = _verify_plugin_type(self.plugin_type)
            return plugin_model
        except TypeError as e:
            logger.exception(e)
            raise TypeError(
                f"A plugin doesn't exist. Plugin: {self.plugin_type}")

    @property
    def plugin_type(self):
        return self.meta.get("plugin_type")

    @plugin_type.setter
    def plugin_type(self, plugin_type):
        self.meta['plugin_type'] = plugin_type

    @property
    def meta(self):
        return self.plugin_fields.get("meta")

    @property
    def non_meta_fields(self):
        return {
            key: value for key, value in self.plugin_fields.items()
            if key != "meta"
        }

    @property
    def parent_id(self):
        return self.meta.get("parent")

    @property
    def position(self):
        return self.meta.get("position")

    @property
    def source_id(self):
        return self.meta.get("id")

    def _get_target_plugin(self, root_target_plugin, plugin_map):
        return root_target_plugin if self.is_root_plugin else plugin_map[self.parent_id]

    def _is_root_plugin(self, plugin_map):
        return self.parent_id not in plugin_map

    def _validate(self):
        if not self.is_root_plugin:
            return
        return self._validate_child() and self._validate_parent()

    def _validate_child(self):
        allowed_children = self._get_allowed_children()
        is_valid = ALL_CHILDREN_ALLOWED in allowed_children or self.plugin_type in allowed_children

        if is_valid:
            return

        msg = f"Plugin type {self.plugin_type} is not allowed as a child of {getattr(self.target_plugin, 'plugin_type', None)}"
        logger.error(msg)
        raise InvalidPluginError(msg)

    def _validate_parent(self):
        allowed_parents = self._get_allowed_parents()
        is_valid = ALL_PARENTS_ALLOWED in allowed_parents or getattr(
            self.target_plugin, 'plugin_type', None) in allowed_parents

        if is_valid:
            return

        msg = f"Plugin {self.plugin_type} requires a parent of type {self._get_allowed_parents()}"
        logger.error(msg)
        raise InvalidPluginError(msg)

    def _get_allowed_children(self):
        child_classes = []

        if hasattr(self.target_plugin, 'get_plugin_class'):
            plugin_class = self.target_plugin.get_plugin_class()
            allow_children = getattr(plugin_class, 'allow_children', False)

            if allow_children:
                child_classes = getattr(plugin_class, 'child_classes', [])

        if self.target_plugin is None or child_classes is None:
            return [ALL_CHILDREN_ALLOWED]

        return child_classes

    def _get_allowed_parents(self):
        try:
            plugin_class = plugin_pool.get_plugin(self.plugin_type)
            parent_classes = getattr(plugin_class(), 'parent_classes', [ALL_PARENTS_ALLOWED])
            return parent_classes
        except KeyError:
            raise TypeError(f"Plugin type '{self.plugin_type}' does not exist in the plugin pool.")
        except Exception as e:
            raise Exception(f"Can't get allowed parents for type '{self.plugin_type}'. Error: {e}")

    def create_dummy_plugin(self):
        try:
            self.plugin_type = self.dummy_plugins_target
        except Exception as e:
            msg = f"Failed to create dummy plugin: {e}"
            logger.error(msg)
            raise PluginCreationError(msg)
        return self._add_plugin()

    def create_plugin(self, method_map):
        """
        Creates a plugin instance from the given fields and returns it.
        First, the non-relation fields are added to the plugin instance. Then, the plugin is updated 
        with the relation fields, since it requires the plugin to be created first to establish the relation.

        """
        non_relation_fields, relation_fields = self._filter_fields()
        processed_initial_fields = handle_special_plugin_fields(non_relation_fields, None, method_map)

        with transaction.atomic():
            new_plugin = self._add_plugin(**processed_initial_fields)

            if relation_fields:
                new_plugin = self._update_new_plugin(new_plugin, relation_fields, method_map)

            return new_plugin

    def _filter_fields(self):
        """
        Filters the fields from the import file between relation and non-relation fields.
        Relation fields are handled after the plugin creation to ensure the relation can be made.

        - Fields that do not exist in the plugin are logged and ignored.
        """
        non_relation_fields = {}
        relation_fields = {}
        model_existing_fields = [field.name for field in self.plugin_model._meta.get_fields(include_parents=False)]
        non_meta_fields = self.non_meta_fields.items()

        for key, value in non_meta_fields:
            if self._is_relation_field(value):
                relation_fields[key] = value
                continue
            if not self._key_exists_in_model(key, model_existing_fields):
                logger.warning(f"Field '{key}' does not exist in plugin type {self.plugin_type} and will be ignored.")
                continue
            non_relation_fields[key] = value
        return non_relation_fields, relation_fields

    def _add_plugin(self, **kwargs):
        """
        Adds a plugin to the placeholder / target plugin and returns it.
        """
        language = self.meta.get("language", 'en')
        try:
            return add_plugin(
                placeholder=self.placeholder,
                plugin_type=self.plugin_type,
                language=language,
                target=self.target_plugin,
                **kwargs
            )
        except Exception as e:
            msg = f'Failed to add plugin {self.plugin_type} to placeholder {self.placeholder}: {e}'
            logger.exception(msg)
            raise PluginCreationError(msg)

    def _is_relation_field(self, value):
        """
        Checks if the given value is a related manager.

        Related managers are not needed for the creation of the instance and 
        are handled after the instance creation to ensure a relation can be made.
        """
        related_types = ['relatedmanager', 'manyrelatedmanager']
        return isinstance(value, dict) and value.get('_type') in related_types

    def _key_exists_in_model(self, key, model_fields):
        """
        Checks if the key is present in the model fields.

        Extra fields that are not present in the model fields are ignored.
        """
        return key in model_fields

    def _update_new_plugin(self, instance, fields, method_map):
        deserialized_fields = handle_special_plugin_fields(fields, instance.id, method_map)
        updated_instance = self._update_plugin_fields(instance, deserialized_fields)
        return updated_instance

    def _update_plugin_fields(self, instance, fields):
        for field_name, value in fields.items():
            setattr(instance, field_name, value)
        instance.save()
        return instance
