from .base import Module, extract_value


class File(Module):
    _name = 'file'

    @extract_value('filename')
    def upload(self, file, return_content=None):
        """Upload a file for use in import functions.

        :param file: file-like object open for reading
        :type file: file
        :param return_content: whether to return the uploaded data as
                part of the response
        :return: random name assigned to file
        """

        res = self._request('upload', {'returnContent': return_content}, file)
        if return_content:
            res['_all'] = True
        return res

    def clear(self, name):
        """Delete a file previously uploaded.

        :param name: name of file returned after upload
        :return: path of deleted file
        """

        return self._request('clear', {'filename': name})['filename']

    # how to get existing files?

    def name_or_upload(self, data):
        """If data is a string, assume it's a filename and return it;
        otherwise assume it's a file, upload it, and return the
        generated filename.

        This is useful inside import functions to allow new and existing
        files.

        :param data: filename or file-like object to upload
        :return: filename
        """

        if isinstance(data, basestring):
            return data

        return self.upload(data, False)
