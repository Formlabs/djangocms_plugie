import json
from django.test import TestCase
from cms.models import Placeholder
from djangocms_plugie.importer.version0.importer import Importer
from .filemetadata import FileMetadata


SLOT_NAME = "test"
TEST_FOLDER = "importer"


class ImporterFileMetadata(FileMetadata):
    test_folder = TEST_FOLDER


class TestImporterVersion0(TestCase):
    def setUp(self):
        self.importer = None

    def load_data_from_file(self, file_metadata: ImporterFileMetadata):
        with open(file_metadata.file_path) as json_file:
            return json.load(json_file)

    def set_up_data(self, folder, file_name, target_plugin=None):
        file_metadata = ImporterFileMetadata(folder, file_name)
        import_data = self.load_data_from_file(file_metadata)

        data = {
            "plugin": target_plugin,
            "placeholder": Placeholder.objects.get_or_create(slot=SLOT_NAME)[0],
            "import_data": import_data
        }
        self.importer = Importer(data=data)

    def assert_plugin_is_bounded(self, plugin):
        self.assertTrue(plugin)
        self.assertTrue(callable(getattr(plugin, "get_bound_plugin", None)))

    def test_import_plugins_non_existing_plugin(self):
        with self.assertRaisesRegex(TypeError, r"A plugin doesn't exist. Plugin: inexisting_plugin"):
            self.set_up_data("bad_data", "inexisting_plugin.json")
            self.importer.import_plugins_to_target()