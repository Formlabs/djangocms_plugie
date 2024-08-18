from datetime import datetime
from django.test import TestCase
from cms.models import Placeholder
from djangocms_plugie.exporter import Exporter


SECTION_PLUGIN_TYPE = 'SectionPlugin'
SLOT_NAME = 'test'


class TestExporter(TestCase):
    def setUp(self):
        self.exporter = Exporter()
        self.placeholder = Placeholder.objects.create(slot=SLOT_NAME)

    def test_exporter_init(self):
        self.assertTrue(isinstance(self.exporter.version, str))
        self.assertEqual(len(self.exporter.version.split(".")), 3)

    def test_serialize_plugins_empty(self):
        plugins = []
        self.assertEqual(self.exporter.serialize_plugins(plugins), [])


    def test_serialize_plugin_invalid_plugin(self):
        with self.assertRaises(ValueError):
            invalid_plugin = {}
            self.exporter.serialize_plugins([invalid_plugin])

    def test_get_serialize_method(self):
        now = datetime.now()
        self.assertEqual(self.exporter.exporter_method_map.get_serialize_method([])(
            ['str', True, 1.0]), ['str', True, 1.0])
        self.assertEqual(self.exporter.exporter_method_map.get_serialize_method({})({"a": 1, "b": None}), {"a": 1, "b": None})
        self.assertEqual(self.exporter.exporter_method_map.get_serialize_method(now)(now), int(now.timestamp()))
