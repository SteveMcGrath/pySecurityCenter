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
        """Deletes a specific repository or group of repositories.

        :param *ids: the id of specified repository

        :return: dict containing the id of the deleted repository
        """

        return self._request('delete', {
            'repositories': [{'id': id} for id in ids]
        })['repositories']

    def import_(self, id, file):
        """Import a repository file.

        :param id: the id of the uploaded repository
        :param file: the file is expected to be an absolute path to a tar.gz

        :return: returns the remote repository details just imported
        """

        return self._request('import', {
            'id': id,
            'file': file
        })

    def export(self, id):
        return self._request('export', {
            'id': id
        }, parse=False).content

    def download(self):
        #TODO repository::download
        raise NotImplementedError

    def get_remote_repositories(self, host):
        """Retrieve repositories available within the database.

        :param host: attribute host is expected to be a valid host IP address

        :return: returns repositories in database
        """

        # return self._request('getRemoteRepositories', {
        #     'repositories': [{'host': host} for host in hosts]
        # })

        return self._request('getRemoteRepositories', {
            'host': host
        })

    def download_remote_repositories(self):
        #TODO repository::downloadRemoteRepositories
        raise NotImplementedError

    def validate_add(self, type, data_format, correlation, remote_type, nessus_type,
                     download_format='v2', org=None, description=None, enable_trend=True,
                     remote_def=None, nessus_def=None):
        """Validate the added repository.

        :param type: the repository type
        :param data_format: repository data format should be IPv4
        :param correlation: need to be a valid repository correlation
        :param remote_type: the schedule type for the repository
        :param nessus_type: the Nessus schedule type for the repository
        :param download_format: need to be a valid download format for Nessus v2
        :param org: the organization associated with the repository
        :param description: repository description
        :param enable_trend: default is set to true
        :param remote_def: the schedule definition for the repository
        :param nessus_def: the Nessus schedule definition for the repository

        :return:
        """

        if org is not None:
            org = [{'id': id} for id in org]

        return self._request('validateAdd', {
            'type': type,
            'organizations': org,
            'dataFormat': data_format,
            'correlation': correlation,
            'enableTrending': enable_trend,
            'remoteScheduleType': remote_type,
            'remoteScheduleDefinition': remote_def,
            'description': description,
            'downloadFormat': download_format,
            'nessusScheduleType': nessus_type,
            'nessusScheduleDefinition': nessus_def
        })

    def validate_edit(self):
        #TODO repository::validateEdit
        raise NotImplementedError

    def generate_nessus_file(self):
        #TODO repository::generateNessusFile
        raise NotImplementedError
