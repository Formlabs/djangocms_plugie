import os

class FileMetadata():
    test_folder = None

    def __init__(self, folder, file_name):
        self.folder = folder
        self.file_name = file_name

    @property
    def file_path(self):
        if self.test_folder is None:
            raise NotImplementedError("Subclasses must set test_folder attribute")
        file_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(file_path, 'fixture', self.test_folder, self.folder, self.file_name)
