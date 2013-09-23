from .base import Module, extract_value


class Repository(Module):
    _name = 'repository'

    @extract_value('repositories')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO repository::add
        raise NotImplementedError

    def edit(self):
        #TODO repository::edit
        raise NotImplementedError

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'repositories': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        return self._request('delete', {
            'repositories': [{'id': id} for id in ids]
        })['assets']

    def import_(self):
        #TODO repository::import
        raise NotImplementedError

    def export(self):
        #TODO repository::export
        raise NotImplementedError

    def download(self):
        #TODO repository::download
        raise NotImplementedError

    def get_remote_repositories(self):
        #TODO repository::getRemoteRepositories
        raise NotImplementedError

    def download_remote_repositories(self):
        #TODO repository::downloadRemoteRepositories
        raise NotImplementedError

    def validate_add(self):
        #TODO repository::validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO repository::validateEdit
        raise NotImplementedError

    def generate_nessus_file(self):
        #TODO repository::generateNessusFile
        raise NotImplementedError
