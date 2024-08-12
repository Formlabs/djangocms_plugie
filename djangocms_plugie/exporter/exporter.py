from djangocms_plugie.methods.method_map import ExporterMethodMap
from djangocms_plugie.exporter.plugin_serializer import PluginSerializer


class Exporter:
    def __init__(self):
        self.version = "0.1.0"
        self.exporter_method_map = ExporterMethodMap(exporter=self)
        self.plugin_serializer = PluginSerializer(self.exporter_method_map)

    def serialize_plugins(self, plugins):
        return [
            serialized_plugin
            for plugin in plugins
            if (serialized_plugin := self.plugin_serializer.serialize_plugin(plugin)) != {}
        ]
