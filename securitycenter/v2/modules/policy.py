from .base import Module, extract_value


class Policy(Module):
    _name = 'policy'

    @extract_value('policies')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO policy::add
        raise NotImplementedError

    def edit(self):
        #TODO policy::edit
        raise NotImplementedError

    def share_simulate(self, id, users):
        return self._request('shareSimulate', {
            'id': id,
            'users': [{'id': u_id} for u_id in users]
        })['effects']

    def share(self, id, users):
        return self._request('share', {
            'id': id,
            'users': [{'id': u_id} for u_id in users]
        })

    def copy(self, id, name):
        return self._request('copy', {'id': id, 'name': name})

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'policies': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        return self._request('delete', {
            'policies': [{'id': id} for id in ids]
        })['policies']

    def download(self, id):
        return self._request('exportNessusPolicy', {
            'id': id
        }, parse=False).content

    def upload(self, file, name=None, visibility='user', description=None,
               group=None):
        #TODO parse xml to fill other fields
        filename = self._sc.file.name_or_upload(file)

        return self._request('importNessusPolicy', {
            'filename': filename,
            'name': name,
            'visibility': visibility,
            'description': description,
            'group': group
        })
