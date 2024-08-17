from djangocms_plugie.methods.exporter_method_map import ExporterMethodMap
from djangocms_plugie.exporter.plugin_serializer import PluginSerializer
from djangocms_plugie import __version__


class Exporter:
    def __init__(self):
        self.version = __version__
        self.exporter_method_map = ExporterMethodMap(exporter=self)
        self.plugin_serializer = PluginSerializer(self.exporter_method_map)

    def serialize_plugins(self, plugins):
        return [
            serialized_plugin
            for plugin in plugins
            if (serialized_plugin := self.plugin_serializer.serialize_plugin(plugin)) != {}
        ]
