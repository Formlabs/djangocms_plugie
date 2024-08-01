import os
import importlib.util
import inspect
import logging
from djangocms_plugie.methods.method_base import MethodBase
from djangocms_plugie.methods.exceptions import (
    CustomMethodsDirectoryNotFoundError,
    BadMethodNameError,
    ModuleLoadError
)
from djangocms_plugie.methods.built_in_deserializers \
    import register_deserializers
from djangocms_plugie.methods.built_in_serializers \
    import register_serializers


logger = logging.getLogger(__name__)
CUSTOM_METHODS_PATH = 'plugie/custom_methods'


class MethodMapBase:
    def __init__(
            self,
            method_name=None,
            custom_methods_path=CUSTOM_METHODS_PATH
    ):
        self.method_map = {}
        self.method_name = method_name
        self.custom_methods_path = custom_methods_path

    def load_custom_methods(self):
        self._validate_inputs()

        for filename in self._list_python_files():
            module = self._load_module(filename)
            if module:
                self._process_module(module)

    def load_builtin_methods(self):
        raise NotImplementedError

    def _validate_inputs(self):
        self._validate_method_name(self.method_name)
        self._validate_custom_methods_path(self.custom_methods_path)

    def _validate_method_name(self, method_name):
        if method_name != 'serialize' and method_name != 'deserialize':
            raise BadMethodNameError(method_name)

    def _validate_custom_methods_path(self, custom_methods_path):
        if not os.path.isdir(custom_methods_path):
            logger.error(f"Custom methods directory '{custom_methods_path}' does not exist.")
            raise CustomMethodsDirectoryNotFoundError(self.custom_methods_path)

    def _list_python_files(self):
        return [f for f in os.listdir(self.custom_methods_path) if f.endswith(".py")]

    def _load_module(self, filename):
        module_path = os.path.join(self.custom_methods_path, filename)
        module_name = filename[:-3]
        try:
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module
        except Exception as e:
            logger.error(f"Error loading module {module_name}: {e}")
            raise ModuleLoadError(module_name, e)

    def _process_module(self, module):
        classes = self._get_classes_from_module(module)
        valid_classes = self._filter_valid_classes(classes)
        self._update_method_map(valid_classes, module)

    def _get_classes_from_module(self, module):
        return [obj for _, obj in inspect.getmembers(module, inspect.isclass)]

    def _filter_valid_classes(self, classes):
        return [cls for cls in classes if issubclass(cls, MethodBase) and cls is not MethodBase]

    def _update_method_map(self, classes, module):
        for cls in classes:
            self._update_method_map_for_class(cls, module)

    def _update_method_map_for_class(self, cls, module):
        for type_name in cls().type_names:
            self._log_override_if_exists(type_name, module)
            self.method_map[type_name] = getattr(cls, self.method_name)

    def _log_override_if_exists(self, type_name, module):
        if type_name in self.method_map:
            logger.info(f"Overriding {self.method_name} for {type_name} with {module.__name__}")


class ImporterMethodMap(MethodMapBase):
    def __init__(self):
        super().__init__(method_name='deserialize')
        self.load_custom_methods()
        self.load_builtin_methods()

    def load_builtin_methods(self):
        method_name = self.method_name
        try:
            register_deserializers(self)
        except ImportError as e:
            logger.error(
                f"Error importing built-in custom {method_name} methods: {e}")


class ExporterMethodMap(MethodMapBase):
    def __init__(self, exporter=None):
        super().__init__(method_name='serialize')
        self.exporter = exporter
        self.load_builtin_methods()
        self.load_custom_methods()

    def load_builtin_methods(self):
        method_name = self.method_name
        try:
            register_serializers(self)
        except ImportError as e:
            logger.error(f"Error importing built-in custom {method_name} methods: {e}")

    def get_serialize_method(self, attr_value):
        serialize_method = self.method_map.get(
            type(attr_value).__name__.lower())
        if serialize_method is not None:
            return serialize_method

        raise ValueError(f'No serialize method found for {type(attr_value).__name__}')
