import logging
from djangocms_plugie.methods.exceptions import LoadBuiltinMethodsError
from djangocms_plugie.methods.built_in_deserializers import register_deserializers
from djangocms_plugie.methods.method_map_base import MethodMapBase



logger = logging.getLogger(__name__)

class ImporterMethodMap(MethodMapBase):
    """
    Method map for the importer.
    
    Methods:
    - load_custom_methods: Load the custom methods
    - load_builtin_methods: Load the built-in methods
    """
    def __init__(self):
        """
        Initialize the ImporterMethodMap.
        """
        super().__init__(method_name='deserialize')
        self.load_custom_methods()
        self.load_builtin_methods()

    def load_builtin_methods(self):
        """
        Load the built-in methods.

        Raises:
            LoadBuiltinMethodsError: If the built-in methods cannot be loaded.
        """
        method_name = self.method_name
        try:
            register_deserializers(self)
        except Exception as e:
            logger.error(f"Error importing built-in custom {method_name} methods: {e}")
            raise LoadBuiltinMethodsError(method_name, e)