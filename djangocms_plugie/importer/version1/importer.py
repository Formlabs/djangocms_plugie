import logging
from djangocms_plugie.config import Config
from djangocms_plugie.importer.version0.plugin_context import PluginContext
from djangocms_plugie.methods.importer_method_map import ImporterMethodMap
from djangocms_plugie import __version__


logger = logging.getLogger(__name__)


class Logger:
    def log(self, level, message):
        logger.log(level, message)

    def info(self, message):
        logger.info(message)


class ImportPluginsError(Exception):
    """Raised when an error occurs during plugin import."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Importer:
    def __init__(self, logger=None, data=None):
        self.logger = logger or Logger()
        self.version = __version__
        self.method_map = ImporterMethodMap().method_map
        self.dummy_plugins = Config().get_dummy_plugins_source()
        self.data = data
        self.plugin_map = {}

    @property
    def placeholder(self):
        return self.data.get('placeholder')

    @property
    def root_target_plugin(self):
        return self.data.get('plugin')

    @property
    def imported_plugins(self):
        try:
            return self.data.get("import_data").get("all_plugins")
        except Exception as e:
            msg = f"Failed to get all plugins from import data: {e}"
            self.logger.info(msg)
            raise ImportPluginsError(msg)

    def import_plugins_to_target(self):
        plugins = self.imported_plugins
        sorted_plugins = self._sort_plugins(plugins)
        self._create_plugin_tree(sorted_plugins)

    def _create_plugin_tree(self, sorted_plugins):
        for plugin_fields in sorted_plugins:
            plugin_context = self._create_plugin_context_from_fields(plugin_fields)
            new_plugin = self._create_plugin_from_context(plugin_context)
            self._update_plugin_map(plugin_context, new_plugin)

    def _update_plugin_map(self, plugin_context, new_plugin):
        original_plugin_id = plugin_context.source_id
        self.plugin_map[original_plugin_id] = new_plugin

    def _create_plugin_context_from_fields(self, plugin_fields):
        return PluginContext(
            plugin_fields,
            self.placeholder,
            self.plugin_map,
            self.root_target_plugin
        )

    def _create_plugin_from_context(self, plugin_context):
        if self._is_dummy_plugin(plugin_context):
            return plugin_context.create_dummy_plugin()
        return plugin_context.create_plugin(self.method_map)

    def _is_dummy_plugin(self, plugin_context):
        return plugin_context.plugin_type in self.dummy_plugins

    def _sort_plugins(self, plugins):
        if not plugins:
            return plugins

        try:
            return sorted(plugins, key=lambda p: (p.get("meta").get("position", 0)))
        except Exception as e:
            msg = f"Failed to sort plugins: {e}"
            self.logger.info(msg)
            raise ImportPluginsError(msg)
