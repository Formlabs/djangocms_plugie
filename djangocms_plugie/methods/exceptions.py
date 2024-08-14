class CustomMethodsDirectoryNotFoundError(FileNotFoundError):
    """Raised when custom methods directory is not found."""

    def __init__(self, path):
        super().__init__(
            f"The directory {path} with custom methods does not exist. Make "
            "sure to run 'plugie <project_dir>', where <project_dir> is the "
            "root directory of your project."
        )


class BadMethodNameError(ValueError):
    """Raised when the method name is invalid."""

    def __init__(self, method_name):
        super().__init__(
            f"Invalid method name: {method_name}. The method name must be "
            "'serialize' or 'deserialize'."
        )


class ModuleLoadError(Exception):
    """Raised when a module cannot be loaded."""

    def __init__(self, module_name, error):
        super().__init__(f"Error loading module {module_name}: {error}")

class LoadBuiltinMethodsError(Exception):
    """Raised when the built-in methods cannot be loaded."""

    def __init__(self, method_name, error):
        super().__init__(f"Error importing built-in custom {method_name} methods: {error}")