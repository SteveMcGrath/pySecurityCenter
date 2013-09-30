from .base import Module, extract_value


class Repository(Module):
    _name = 'repository'

    @extract_value('repositories')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO: repository::add
        raise NotImplementedError

    def edit(self):
        #TODO: repository::edit
        raise NotImplementedError

    def delete(self, *ids):
        """Deletes a specified repository by ID.

        :param ids: repository ID

        :return param
        """

        return self._request('delete', {
            'repository': [{'id': id} for id in ids]
        })

    def import_repository(self):
        #TODO: repository::import_repository
        raise NotImplementedError

    def export(self):
        #TODO: repository::export
        raise NotImplementedError

    def download(self):
        #TODO: repository::download
        raise NotImplementedError

    def get_remote_repositories(self):
        #TODO: repository::get_remote_repositories
        raise NotImplementedError

    def download_remote_repository(self):
        #TODO: repository::download_remote_repository
        raise NotImplementedError

    def validate_add(self):
        #TODO: repository::validate_add
        raise NotImplementedError

    def validate_edit(self):
        #TODO: repository::validate_edit
        raise NotImplementedError

    def generate_nessus_file(self):
        #TODO: repository::generate_nessus_file
        raise NotImplementedError
