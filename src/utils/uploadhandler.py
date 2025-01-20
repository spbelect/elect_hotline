
from django.core.files.uploadhandler import FileUploadHandler, StopUpload, SkipFile
from django.conf import settings

MB = 2**20


class QuotaUploadHandler(FileUploadHandler):
    """ This upload handler terminates the connection if more than a quota
        is uploaded. """

    def __init__(self, request=None):
        super(QuotaUploadHandler, self).__init__(request)
        self.quota = settings.MAX_UPLOAD_FILES_SIZE_MB * MB
        self.total_upload = 0

    def receive_data_chunk(self, raw_data, start):
        self.total_upload += len(raw_data)
        if self.total_upload >= self.quota:
            #raise StopUpload(connection_reset=True)
            raise SkipFile()
        return raw_data

    def file_complete(self, file_size):
        return None

 

#class CustomUploadError(Exception):
    #pass

#class ErroringUploadHandler(FileUploadHandler):
    #"""A handler that raises an exception."""
    #def receive_data_chunk(self, raw_data, start):
        #print 123
        #raise SkipFile()