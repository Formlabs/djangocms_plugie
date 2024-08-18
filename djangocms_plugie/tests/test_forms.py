from django.test import TestCase
from cms.models import Placeholder
from django.core.files.uploadedfile import SimpleUploadedFile
from djangocms_plugie.forms import ImportForm
from .filemetadata import FileMetadata

TEST_FOLDER = "forms"


class FormsFileMetadata(FileMetadata):
    test_folder = TEST_FOLDER


class TestImportForm(TestCase):
    def setUp(self):
        self.setup_placeholder()
        self.setup_form_data()

    def setup_placeholder(self):
        self.placeholder = Placeholder.objects.create(slot="test")

    def setup_form_data(self):
        self.data = {
            'plugin': None,
            'placeholder': self.placeholder.id,
        }
        self.initial = {
            'placeholder': self.placeholder,
            'plugin': None,
        }
        self.form = ImportForm

    def setup_form(self, file_metadata: FormsFileMetadata):
        files = self.create_file_from_path(file_metadata)
        return self.form(data=self.data, files=files, initial=self.initial)

    @staticmethod
    def create_file_from_path(file_metadata: FormsFileMetadata):
        with open(file_metadata.file_path, 'rb') as f:
            file_content = f.read()

        uploaded_file = SimpleUploadedFile(
            name=file_metadata.file_name,
            content=file_content,
            content_type='application/json',
        )

        return {'import_file': uploaded_file}

    def test_import_form_file_is_list(self):
        file_metadata = FormsFileMetadata("bad_data", "file_is_list.json")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())
        error_message = "File is not valid: the Import file must be a dictionary with keys 'version' and 'all_plugins'"
        self.assertTrue(any(error_message in error for error in form.errors.values()))

    def test_import_file_missing_version_key(self):
        file_metadata = FormsFileMetadata("bad_data", "missing_version_key.json")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())
        error_message = "File is not valid: the Import file must be a dictionary with keys 'version' and 'all_plugins'"
        self.assertTrue(any(error_message in error for error in form.errors.values()))

    def test_import_non_existing_version(self):
        file_metadata = FormsFileMetadata("bad_data", "non_existing_version.json")
        form = self.setup_form(file_metadata)
        self.assertTrue(form.is_valid())
        with self.assertRaisesRegex(TypeError, r"Error importing module"):
            form.run_import()

    def test_import_plugin_missing_meta_key(self):
        file_metadata = FormsFileMetadata("bad_data", "plugin_missing_meta_key.json")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())
        error_message = "File is not valid: a plugin is missing 'meta' key"
        self.assertTrue(any(error_message in error for error in form.errors.values()))

    def test_import_plugin_missing_required_meta_attributes(self):
        file_metadata = FormsFileMetadata("bad_data", "plugin_missing_required_meta_attributes.json")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())

    def test_import_version_bad_type(self):
        file_metadata = FormsFileMetadata("bad_data", "version_bad_type.json")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())
        error_message = "File is not valid: 'version' is not a string with format 'x.y.z'"
        self.assertTrue(any(error_message in error for error in form.errors.values()))

    def test_import_version_non_json(self):
        file_metadata = FormsFileMetadata("bad_data", "non_json.jsonc")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())

    def test_import_version_empty_file(self):
        file_metadata = FormsFileMetadata("bad_data", "empty_file.json")
        form = self.setup_form(file_metadata)
        self.assertFalse(form.is_valid())
        error_message = 'The submitted file is empty.'
        self.assertTrue(form.errors['import_file'], error_message)



class FileContentEmptyError(ValueError):
    pass


class InvalidJSONContentError(ValueError):
    pass
