from .base import Module, extract_value


class Scanner(Module):
    _name = 'scanner'

    @extract_value('scanners')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO scanner::add
        raise NotImplementedError

    def edit(self):
        #TODO scanner::edit
        raise NotImplementedError

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'scanner': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        """Deletes a specific scanner.

        :param *ids: the id of specified scanner

        :return: dict containing the id of the deleted scanner
        """

        return self._request('delete', {
            'scanner': [{'id': id} for id in ids]
        })['scanner']

    def update_status(self):
        return self._request('updateStatus')

    def get_cert_info(self, id):
        return self._request('getCertInfo', {
            'scannerID': id
        })

    def validate_add(self, description=None, zones=None, username=None,
                     password=None, host=True, manage=False, enabled=True,
                     cert=None):
        """Validate adding a scanner.

        :param description: description for scanner
        :param zones: zone associated with the scanner
        :param username: login username for scanner
        :param password: login password for scanner
        :param host: verified host for the scanner
        :param manage: manage plugins
        :param enabled: is the scanner enabled
        :param cert: valid cert used for the scanner

        :return: return valid added scanner information
        """

        if zones is not None:
            zones = [{'id': id} for id in zones]

        return self._request('validateAdd', {
            'description': description,
            'zones': zones,
            'username': username,
            'password': password,
            'verifyHost': host,
            'managePlugins': manage,
            'enabled': enabled,
            'cert': cert
        })

    def validate_edit(self, s_id, ip, name, description, port, host, manage=False,
                      enabled=True, cert=None, username=None, zones=None):
        """Validate editing a scanner.

        :param s_id: id of edited scanner
        :param ip: valid IP address for the scanner
        :param name: Scanner name
        :param description: description for scanner
        :param port: port used
        :param host: verified host for the scanner
        :param manage: manage plugins
        :param enabled: is the scanner enabled ?
        :param cert: valid cert used for the scanner
        :param username: login username for scanner
        :param zones: zone associated with the scanner

        :return: return valid edited scanner information
        """

        if zones is not None:
            zones = [{'id': id} for id in zones]

        return self._request('validateEdit', {
            'scannerID': s_id,
            'ip': ip,
            'name': name,
            'description': description,
            'port': port,
            'verifyHost': host,
            'managePlugins': manage,
            'enabled': enabled,
            'cert': cert,
            'username': username,
            'zones': zones
        })


class PassiveScanner(Module):
    _name = 'passiveScanner'

    def init(self):
        return self._request('init')

    def add(self):
        #TODO scan::add
        raise NotImplementedError

    def edit(self):
        #TODO scan::edit
        raise NotImplementedError

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'passiveScanner': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        """Deletes a specific passive scanner.

        :param *ids: the id of specified passive scanner

        :return: dict containing the id of the deleted passive scanner
        """

        return self._request('delete', {
            'passiveScanner': [{'id': id} for id in ids]
        })['passiveScanner']

    def update_status(self):
        return self._request('updateStatus')

    def validate_add(self, ip, name, port, description=None, repos=None,
                     username=None, password=None):
        """Validate the added passive scanner.

        :param ip: valid IP address for passive scanner
        :param name: name for the passive scanner
        :param port: valid port for the passive scanner
        :param description: description for the passive scanner
        :param repos: array of repository ID associated with passive scanner
        :param username: login username for passive scanner
        :param password: login password for passive scanner

        :return: return params used for adding
        """

        if repos is not None:
            repos = [{'id': id} for id in repos]

        return self._request('validateAdd', {
            'ip': ip,
            'name': name,
            'port': port,
            'description': description,
            'repositories': repos,
            'username': username,
            'password': password
        })

    def validate_edit(self, s_id, ip, name, port, username, password,
                      description, repos=None):
        """Validate the edited passive scanner.

        :param s_id: the passive scanner id
        :param ip: valid IP address when editing a passive scanner
        :param name: name for the passive scanner
        :param port: port for the passive scanner
        :param username: login username for the passive scanner
        :param password: login password for the passive scanner
        :param description: passive scanner description
        :param repos: an array of repository ID associated with passive scanner

        :return: return params used for editing
        """

        if repos is not None:
            repos = [{'id': id} for id in repos]

        return self._request('validateEdit', {
            'scannerID': s_id,
            'ip': ip,
            'name': name,
            'port': port,
            'username': username,
            'password': password,
            'description': description,
            'repositories': repos
        })