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
