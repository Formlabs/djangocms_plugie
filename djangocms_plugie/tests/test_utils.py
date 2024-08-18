import unittest
import json
from io import BytesIO
from django.core.exceptions import ValidationError
from djangocms_plugie.utils import parse_import_file, extract_major_version, get_module_name, validate_parsed_data_structure, validate_all_plugins, validate_plugin_meta, REQUIRED_META_KEYS

class TestGetParsedData(unittest.TestCase):

    def test_parse_import_file_valid(self):
        file_content = b'{"key": "value"}'
        file_obj = BytesIO(file_content)
        result = parse_import_file(file_obj)
        self.assertEqual(result, {"key": "value"})

    def test_parse_import_file_invalid_json(self):
        file_content = b'invalid json'
        file_obj = BytesIO(file_content)
        with self.assertRaises(ValidationError):
            parse_import_file(file_obj)

class TestExtractMajorVersion(unittest.TestCase):

    def test_extract_major_version_valid(self):
        version = "1.2.3"
        result = extract_major_version(version)
        self.assertEqual(result, "1")

    def test_extract_major_version_invalid(self):
        version = "invalid_version"
        with self.assertRaises(ValueError):
            extract_major_version(version)

    def test_extract_major_version_empty(self):
        version = ""
        with self.assertRaises(ValueError):
            extract_major_version(version)
    
    def test_extract_major_version_none(self):
        version = None
        with self.assertRaises(ValueError):
            extract_major_version(version)

    def test_get_module_name_valid(self):
        self.assertEqual(get_module_name("0"), "djangocms_plugie.importer.version0.importer")
        self.assertEqual(get_module_name("1"), "djangocms_plugie.importer.version1.importer")
        self.assertEqual(get_module_name("2"), "djangocms_plugie.importer.version2.importer")
        self.assertEqual(get_module_name("10"), "djangocms_plugie.importer.version10.importer")

    def test_get_module_name_invalid(self):
        with self.assertRaises(ValueError):
            get_module_name("")
        with self.assertRaises(ValueError):
            get_module_name(" ")
        with self.assertRaises(TypeError):
            get_module_name(None)
        with self.assertRaises(TypeError):
            get_module_name(1)

class TestValidateParsedDataStructure(unittest.TestCase):

    def test_valid_data(self):
        data = {
            "version": "1.0.0",
            "all_plugins": []
        }
        try:
            validate_parsed_data_structure(data)
        except ValidationError:
            self.fail("validate_parsed_data_structure raised ValidationError unexpectedly!")

    def test_data_not_dict(self):
        data = ["version", "all_plugins"]
        with self.assertRaises(ValidationError):
            validate_parsed_data_structure(data)

    def test_missing_version_key(self):
        data = {
            "all_plugins": []
        }
        with self.assertRaises(ValidationError):
            validate_parsed_data_structure(data)

    def test_missing_all_plugins_key(self):
        data = {
            "version": "1.0.0"
        }
        with self.assertRaises(ValidationError):
            validate_parsed_data_structure(data)

class TestValidateAllPlugins(unittest.TestCase):

    def test_valid_plugins(self):
        all_plugins = [
            {"meta": {"parent": None, "id": 1, "position": 0, "plugin_type": "TextPlugin", "depth": 0}}
        ]
        try:
            validate_all_plugins(all_plugins)
        except ValidationError:
            self.fail("validate_all_plugins raised ValidationError unexpectedly!")

    def test_all_plugins_not_list(self):
        all_plugins = "not a list"
        with self.assertRaises(ValidationError):
            validate_all_plugins(all_plugins)

    def test_all_plugins_empty_list(self):
        all_plugins = []
        with self.assertRaises(ValidationError):
            validate_all_plugins(all_plugins)

class TestValidatePluginMeta(unittest.TestCase):

    def test_valid_plugin_meta(self):
        plugin = {"meta": {"parent": None, "id": 1, "position": 0, "plugin_type": "TextPlugin", "depth": 0}}
        try:
            validate_plugin_meta(plugin, REQUIRED_META_KEYS)
        except ValidationError:
            self.fail("validate_plugin_meta raised ValidationError unexpectedly!")

    def test_plugin_missing_meta_key(self):
        for key in REQUIRED_META_KEYS:
            plugin = {"meta": {k: None for k in REQUIRED_META_KEYS if k != key}}
            with self.assertRaises(ValidationError):
                validate_plugin_meta(plugin, REQUIRED_META_KEYS)

    def test_plugin_meta_not_dict(self):
        plugin = {"meta": "not a dict"}
        with self.assertRaises(ValidationError):
            validate_plugin_meta(plugin, REQUIRED_META_KEYS)

if __name__ == '__main__':
    unittest.main()