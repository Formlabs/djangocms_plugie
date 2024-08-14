import os
import importlib.util
import inspect
import logging
from typing import Any, Literal, Type, List, Optional
from types import ModuleType
from djangocms_plugie.config import Config
from djangocms_plugie.methods.method_base import MethodBase
from djangocms_plugie.methods.exceptions import (
    CustomMethodsDirectoryNotFoundError,
    BadMethodNameError,
    ModuleLoadError
)


logger = logging.getLogger(__name__)

class InvalidInputError(Exception):
    """Raised when the inputs to the Method Map are invalid."""

    def __init__(self, message):
        super().__init__(f'Invalid inputs when loading custom methods to the method map: {message}')


class MethodMapBase:
    """
    Base class for the method map.
    
    Attributes:
    - method_map: dict, the map of method names to the method functions
    - method_name: str, the method name to load: 'serialize' or 'deserialize'
    - custom_methods_path: str, the path to the custom methods directory
    
    Methods:
    - load_custom_methods: Load the custom methods from the custom methods directory
    - load_builtin_methods: Load the built-in methods
    - _validate_inputs: Validate the inputs
    - _validate_method_name: Validate the method name
    - _validate_custom_methods_path: Validate the custom methods path
    - _list_python_files: List the python files in the custom methods directory
    - _load_module: Load the module from the file
    - _process_module: Process the module
    - _get_classes_from_module: Get the classes from the module
    - _filter_valid_classes: Filter the valid classes
    - _update_method_map: Update the method map
    - _update_method_map_for_class: Update the method map for the class
    - _log_override_if_exists: Log the override if the method already exists
    """
    def __init__(
            self,
            method_name: Literal['serialize', 'deserialize'],
            custom_methods_path: Optional[str]=Config().get_custom_methods_path()
    ):
        """
        Initialize the MethodMapBase.

        :param method_name: str, the method name to load: 'serialize' or 'deserialize'
        :param custom_methods_path: Optional[str], the path to the custom methods directory
        """
        self.method_map = {}
        self.method_name = method_name
        self.custom_methods_path: str = custom_methods_path

    def load_custom_methods(self) -> None:
        """"
        Load the custom methods from the custom methods directory.
        
        Raises:
            InvalidInputError: If any of the inputs are invalid.
            ModuleLoadError: If a module cannot be loaded.
        """
        self._validate_inputs()

        for filename in self._list_python_files():
            module = self._load_module(filename)
            if module:
                self._process_module(module)

    def load_builtin_methods(self) -> None:
        """
        Load the built-in methods. This method should be implemented in the child class.
        
        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def _validate_inputs(self) -> None:
        """
        Validate the inputs.
        
        Raises:
            InvalidInputError: If the inputs are invalid.
        """
        try:
            self._validate_method_name(self.method_name)
            self._validate_custom_methods_path(self.custom_methods_path)
        except Exception as e:
            logger.error(f"Invalid inputs when loading custom methods to the method map: {e}")
            raise InvalidInputError(e)

    def _validate_method_name(self, method_name: str) -> None:
        """
        Validate the method name.
        
        :param method_name: str, the method name
        
        Raises:
            BadMethodNameError: If the method name is not 'serialize' or 'deserialize'.
        """
        if method_name != 'serialize' and method_name != 'deserialize':
            raise BadMethodNameError(method_name)

    def _validate_custom_methods_path(self, custom_methods_path):
        """
        Validate the custom methods path.
        
        :param custom_methods_path: str, the path to the custom methods directory
        
        Raises:
            CustomMethodsDirectoryNotFoundError: If the custom methods directory does not exist.
        """
        if not os.path.isdir(custom_methods_path):
            logger.error(f"Custom methods directory '{custom_methods_path}' does not exist.")
            raise CustomMethodsDirectoryNotFoundError(self.custom_methods_path)

    def _list_python_files(self) -> List[str]:
        """
        List the python files in the custom methods directory.
        
        :return: list, the list of python files
        """
        return [f for f in os.listdir(self.custom_methods_path) if f.endswith(".py")]

    def _load_module(self, filename: str) -> ModuleType:
        """
        Load the module from the file.
        
        :param filename: str, the filename of the module
        
        :return: ModuleType object
        """
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

    def _process_module(self, module: ModuleType) -> None:
        """
        Process the module, extracting the classes and updating the method map.
        
        :param module: ModuleType object
        
        Raises:
            ModuleLoadError: If a module cannot be loaded.
        """
        classes = self._get_classes_from_module(module)
        valid_classes = self._filter_valid_classes(classes)
        self._update_method_map(valid_classes, module)

    def _get_classes_from_module(self, module: ModuleType) -> List[Type[Any]]:
        """
        Get all classes from the module.

        :param module: ModuleType object

        :return: list, the list of classes
        """
        return [obj for _, obj in inspect.getmembers(module, inspect.isclass)]

    def _filter_valid_classes(self, classes: List[Type[Any]]) -> List[Type[MethodBase]]:
        """
        Filter classes to include only those that are subclasses of MethodBase.

        :param classes: list, the list of classes

        :return: list, the list of valid classes, i.e. subclasses of MethodBase
        """
        return [cls for cls in classes if issubclass(cls, MethodBase) and cls is not MethodBase]

    def _update_method_map(self, classes: List[Type[MethodBase]], module: ModuleType) -> None:
        """
        Update the method map with the classes from the module.

        :param classes: list, the list of valid classes
        :param module: ModuleType object
        """
        for cls in classes:
            self._update_method_map_for_class(cls, module)

    def _update_method_map_for_class(self, cls: Type[MethodBase], module: ModuleType) -> None:
        """
        Update the method map for the class.

        :param cls: a subclass of MethodBase
        :param module: ModuleType object
        """
        for type_name in cls().type_names:
            self._log_override_if_exists(type_name, module)
            self.method_map[type_name] = getattr(cls, self.method_name)

    def _log_override_if_exists(self, type_name: str, module: ModuleType) -> None:
        """
        Log the override if the method already exists.

        :param type_name: str, the type name
        :param module: ModuleType object
        """
        if type_name in self.method_map:
            logger.info(f"Overriding {self.method_name} for {type_name} with {module.__name__}")

