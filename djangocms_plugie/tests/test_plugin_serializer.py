from django.test import TestCase
from djangocms_plugie.exporter.plugin_serializer import PluginSerializer
from unittest.mock import MagicMock
from cms.models import CMSPlugin

class TestPluginSerializer(TestCase):
    def setUp(self):
        self.exporter_method_map = MagicMock()
        self.serializer = PluginSerializer(self.exporter_method_map)

    def test_serialize_plugin(self):
        pass

    def test__get_downcasted_plugin_not_cmsplugin_instance(self):
        mock_plugin = MagicMock()
        mock_plugin._meta = MagicMock()
        result = self.serializer._get_downcasted_plugin(mock_plugin)
        self.assertEqual(result, mock_plugin)


    def test__get_plugin_instance(self): 
        mock_plugin = MagicMock(spec=CMSPlugin)
        mock_instance = MagicMock()
        mock_plugin.get_plugin_instance.return_value = [mock_instance, mock_plugin]

        result = self.serializer._get_downcasted_plugin(mock_plugin)
        self.assertEqual(result, mock_instance)

    def test__get_serialized_value(self):
        mock_plugin = MagicMock(spec=CMSPlugin)
        mock_plugin.field1 = 'value1'
        self.exporter_method_map.get_serialize_method.return_value = MagicMock()

        self.serializer._get_serialized_value(mock_plugin, 'field1')

        self.exporter_method_map.get_serialize_method.assert_called_with('value1')



