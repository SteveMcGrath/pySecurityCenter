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

        :return: return repositories available in database
        """

        #TODO repository::getRemoteRepositories
        raise NotImplementedError

    def download_remote_repositories(self):
        #TODO repository::downloadRemoteRepositories
        raise NotImplementedError

    def validate_add(self, type, data_format, correlation, remote_type, nessus_type,
                     download_format='v2', org=None, description=None, enable_trend=True,
                     remote_def=None, nessus_def=None):
        """Validate adding a repository.

        :param type: the repository type
        :param data_format: repository data format should be IPv4
        :param correlation: need to be a valid repository correlation
        :param remote_type: the schedule type for the repository
        :param nessus_type: the Nessus schedule type for the repository
        :param download_format: need to be a valid download format for Nessus v2
        :param org: dict of organization id
        :param description: repository description
        :param enable_trend: default is set to true
        :param remote_def: the schedule definition for the repository
        :param nessus_def: the Nessus schedule definition for the repository

        :return: return valid added repository information
        """

        #include correlation LCELib section?

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

    def validate_edit(self, repos_id, type, name, description, ip, correlation,
                      remote_id, remote_ip, remote_type, nessus_type, download_format='v2',
                      org=None, remote_def=None, nessus_def=None):
        """Validate editing a repository.

        :param repos_id: the repository id
        :param type: the repository type
        :param name: the repository name
        :param description: the repository description
        :param ip: valid IP address in IPv4 or IPv6 depending on data_format
        :param correlation: need to be a valid repository correlation
        :param remote_id: the repository remote id
        :param remote_ip: the repository remote ip
        :param remote_type: the schedule type for the repository (default set to never)
        :param nessus_type: Nessus schedule type (default set to never)
        :param download_format: need to be a valid download format for Nessus v2
        :param org: dict of organization id
        :param remote_def: schedule definition for the repository
        :param nessus_def: Nessus schedule definition for the repository

        :return: return valid edited repository information
        """

        #include correlation LCELib section?

        if org is not None:
            org = [{'id': id} for id in org]

        return self._request('validateEdit', {
            'repID': repos_id,
            'type': type,
            'name': name,
            'organizations': org,
            'description': description,
            'ipRange': ip,
            'correlation': correlation,
            'remoteID': remote_id,
            'remoteIP': remote_ip,
            'downloadFormat': download_format,
            'remoteScheduleType': remote_type,
            'remoteScheduleDefinition': remote_def,
            'nessusScheduleType': nessus_type,
            'nessusScheduleDefinition': nessus_def
        })

    def generate_nessus_file(self):
        #TODO repository::generateNessusFile
        raise NotImplementedError

    def import_repository(self):
        #TODO: repository::import_repository
        raise NotImplementedError
