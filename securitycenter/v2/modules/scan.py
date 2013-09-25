from calendar import timegm
from datetime import datetime
from StringIO import StringIO
from zipfile import ZipFile
from .base import Module, extract_value


class Scan(Module):
    _name = 'scan'

    @extract_value('scans')
    def init(self):
        return self._request('init')

    @extract_value('scan')
    def add(self, name, repo, description=None, freq='template', when=None,
            assets=None, ips=None, policy=None, plugin=None, zone=None,
            credentials=None, mail_launch=None, mail_finish=None,
            mitigated_age=None, track_ip=None, virtual=None, timeout=None,
            reports=None):
        assets = assets or []
        ips = ','.join(ips or [])
        credentials = credentials or []
        reports = reports or []

        if plugin is not None:
            type = 'plugin'
            policyID = None
        else:
            type = 'policy'
            policyID = policy
            policy = None

        return self._request('add', {
            'name': name, 'description': description, 'repositoryID': repo,
            'scheduleFrequency': freq, 'scheduleDefinition': when,
            'assets': [{'id': a_id} for a_id in assets], 'ipList': ips,
            'type': type, 'policyID': policyID, 'policy': policy,
            'pluginID': plugin, 'zoneID': zone,
            'credentials': [{'id': c_id} for c_id in credentials],
            'emailOnLaunch': mail_launch, 'emailOnFinish': mail_finish,
            'classifyMitigatedAge': mitigated_age, 'dhcpTracking': track_ip,
            'scanningVirtualHosts': virtual, 'timeout': timeout,
            'reports': [{'id': r_id} for r_id in reports]
        })

    def edit(self):
        #TODO scan::edit
        raise NotImplementedError

    @extract_value('scan')
    def copy(self, id, name):
        return self._request('copy', {'id': id, 'name': name})

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'scans': [{'id': s_id} for s_id in ids]
        })['effects']

    def delete(self, *ids):
        return self._request('delete', {
            'scans': [{'id': s_id} for s_id in ids]
        })['scans']

    @extract_value('scanResult')
    def launch(self, id):
        return self._request('launch', {'scanID': id})

    def pause(self, result):
        return self._request('pause', {'scanResultID': result})['scanResults']

    def resume(self, result):
        return self._request('resume', {'scanResultID': result})['scanResults']

    def stop(self, result, type='discard'):
        # possible values for type: discard, import, rollover
        return self._request('stop', {'scanResultID': result, 'type': type})


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

    def validate_add(self, auth, description=None, zones=None, username=None,
                     password=None, verify_host=True, manage=False, enabled=True,
                     cert=None):
        """Validate adding a scanner.

        :param auth: authorization type for the scanner
        :param description: description for scanner
        :param zones:
        :param username: login username for scanner
        :param password: login password for scanner
        :param verify_host:
        :param manage: manage plugins
        :param enabled: is the scanner enabled
        :param cert: valid cert used for the scanner

        :return: return valid added scanner information
        """

        if zones is not None:
            zones = [{'id': id} for id in zones]

        return self._request('validateAdd', {
            'authType': auth,
            'description': description,
            'zones': zones,
            'username': username,
            'password': password,
            'verifyHost': verify_host,
            'managePlugins': manage,
            'enabled': enabled,
            'cert': cert
        })

    def validate_edit(self):
        #TODO scanner::validateEdit
        raise NotImplementedError


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


class ScanResult(Module):
    _name = 'scanResult'

    @extract_value('scanResults')
    def init(self):
        return self._request('init')

    def get_range(self, start=None, end=None, user=None):
        if isinstance(start, datetime):
            start = timegm(start.utctimetuple())

        if isinstance(end, datetime):
            end = timegm(end.utctimetuple())

        return self._request('getRange', {
            'startTime': start,
            'endTime': end,
            'userID': user
        })['scanResults']

    def get_progress(self, id):
        return self._request('getProgress', {'scanResultID': id})

    def download(self, id, type='v2'):
        r = self._request('download', {
            'scanResultID': id,
            'downloadType': type
        }, parse=False)

        z = ZipFile(StringIO(r.content))
        return z.read(z.namelist()[0])

    def import_(self, id, mitigated_age=None, track_ip=None, virtual=None):
        return self._request('import', {
            'scanResultID': id,
            'classifyMitigatedAge': mitigated_age,
            'dhcpTracking': track_ip,
            'scanningVirtualHosts': virtual
        })

    def delete(self, *ids):
        return self._request('delete', {
            'scanResults': [{'id': id} for id in ids]
        })['scanResults']


class NessusResults(Module):
    _name = 'nessusResults'  # why is this one plural?

    def upload(self, file, repo, mitigated_age=None, track_ip=None,
               virtual=None):
        filename = self._sc.file.name_or_upload(file)

        return self._request('upload', {
            'filename': filename,
            'repID': repo,
            'classifyMitigatedAge': mitigated_age,
            'dhcpTracking': track_ip,
            'scanningVirtualHosts': virtual
        })
