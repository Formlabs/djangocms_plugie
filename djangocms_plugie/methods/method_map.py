import os
import importlib.util
import inspect
import logging
from djangocms_plugie.methods.method_base import MethodBase
from djangocms_plugie.methods.built_in_deserializers \
    import register_deserializers
from djangocms_plugie.methods.built_in_serializers \
    import register_serializers


logger = logging.getLogger(__name__)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_METHODS_PATH = os.path.join(CURRENT_DIR, 'custom_methods')


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
        method_name = self.method_name
        path = self.custom_methods_path
        self._validate_method_name(method_name)

        if path and os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.endswith(".py"):
                    module_path = os.path.join(path, filename)
                    module_name = filename[:-3]
                    spec = importlib.util.spec_from_file_location(
                        module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                    except Exception as e:
                        logger.error(
                            f"Error loading module {module_name}: {e}")
                        continue

                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, MethodBase) and
                            obj is not MethodBase
                        ):
                            for type_name in obj().type_names:
                                if type_name in self.method_map:
                                    logger.info(
                                        f"Overriding {method_name} for \
                                        {type_name} with {module_name}")
                                self.method_map[type_name] = getattr(
                                    obj, method_name)

    def load_builtin_methods(self):
        raise NotImplementedError

    def _validate_method_name(self, method_name):
        if method_name != 'serialize' and method_name != 'deserialize':
            raise ValueError(f"Invalid method name: {method_name}")


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
            logger.error(
                f"Error importing built-in custom {method_name} methods: {e}")

    def get_serialize_method(self, attr_value):
        serialize_method = self.method_map.get(
            type(attr_value).__name__.lower())
        if serialize_method is not None:
            return serialize_method

        raise ValueError(
            f'No serialize method found for {type(attr_value).__name__}')
