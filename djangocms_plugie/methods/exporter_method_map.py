import logging
from typing import Any, Callable
from djangocms_plugie.methods.built_in_serializers import register_serializers
from djangocms_plugie.methods.method_map_base import MethodMapBase
from djangocms_plugie.methods.exceptions import LoadBuiltinMethodsError


logger = logging.getLogger(__name__)

class ExporterMethodMap(MethodMapBase):
    """
    Method map for the exporter.
    
    Attributes:
    - exporter: Exporter, the exporter object
    
    Methods:
    - load_builtin_methods: Load the built-in methods
    - get_serialize_method: Get the serialize method
    """
    def __init__(self, exporter):
        """
        Initialize the ExporterMethodMap.
        
        :param exporter: Exporter, the exporter object
        """
        super().__init__(method_name='serialize')
        self.exporter = exporter
        self.load_builtin_methods()
        self.load_custom_methods()

    def load_builtin_methods(self) -> None:
        """
        Load the built-in methods.
        
        Raises:
            LoadBuiltinMethodsError: If the built-in methods cannot be loaded.
        """
        method_name = self.method_name
        try:
            register_serializers(self)
        except Exception as e:
            logger.error(f"Error importing built-in custom {method_name} methods: {e}")
            raise LoadBuiltinMethodsError(method_name, e)

    def get_serialize_method(self, attr_value: Any) -> Callable[..., Any]:
        """
        Get the serialize method for the attribute value.

        :param attr_value: Any, the attribute value

        :return: Callable, the serialize method
        """
        serialize_method = self.method_map.get(type(attr_value).__name__.lower())
        if serialize_method is not None:
            return serialize_method

        raise ValueError(f'No serialize method found for {type(attr_value).__name__}')
