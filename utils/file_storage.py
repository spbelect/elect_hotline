from django.core.files.storage import FileSystemStorage
import os

class ReplacingFileStorage(FileSystemStorage):
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(self.path(name))
        return name