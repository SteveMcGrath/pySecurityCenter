from .base import Module, extract_value


class Credential(Module):
    _name = 'credential'

    @extract_value('credentials')
    def init(self):
        return self._request('init')

    def add(
            self, name, type,
            description=None, group=None, visibility='user', users=None,
            **kwargs
    ):
        if users is not None:
            users = [{'id': u_id} for u_id in users]

        kwargs.update({
            'name': name,
            'type': type,
            'description': description,
            'group': group,
            'visibility': visibility,
            'users': users
        })

        return self._request('add', kwargs)

    def add_ssh(
            self, name,
            username, password=None,
            public_key=None, private_key=None, passphrase=None,
            escalation_type=None, escalation_username=None,
            escalation_password=None,
            description=None, group=None, visibility='user', users=None
    ):
        if public_key is not None and private_key is not None:
            public_key = self._sc.file.name_or_upload(public_key)
            private_key = self._sc.file.name_or_upload(private_key)

        return self.add(
            name, 'ssh', description, group, visibility, users,
            username=username, password=password,
            publicKey=public_key,
            privateKey=private_key, passphrase=passphrase,
            privilegeEscalation=escalation_type,
            escalationUsername=escalation_username,
            escalationPassword=escalation_password
        )

    def add_windows(
            self, name,
            username, password, domain=None,
            description=None, group=None, visibility='user', users=None
    ):
        return self.add(
            name, 'windows', description, group, visibility, users,
            username=username, password=password, domain=domain
        )

    def add_snmp(
            self, name,
            community,
            description=None, group=None, visibility='user', users=None
    ):
        return self.add(
            name, 'snmp', description, group, visibility, users,
            communityString=community
        )

    def add_kerberos(
            self, name,
            ip, port, protocol, realm,
            description=None, group=None, visibility='user', users=None
    ):
        return self.add(
            name, 'kerberos', description, group, visibility, users,
            ip=ip, port=port, protocol=protocol, realm=realm
        )

    def edit(
            self, id, prefill=True, name=None, type=None,
            description=None, group=None, visibility=None, users=None,
            **kwargs
    ):
        if users is not None:
            users = [{'id': u_id} for u_id in users]

        if prefill:
            if isinstance(prefill, bool):
                input = dict(
                    (int(c['id']), c) for c in self.init()['credentials']
                )[int(id)]
            else:
                input = dict(prefill)
        else:
            input = {'id': id}

        kwargs.update({
            'name': name,
            'type': type,
            'description': description,
            'group': group,
            'visibility': visibility,
            'users': users
        })
        kwargs = dict(
            (key, value) for key, value in kwargs.iteritems()
            if value is not None
        )
        input.update(kwargs)

        return self._request('edit', input)

    def edit_ssh(
            self, id, prefill=True, name=None,
            username=None, password=None,
            public_key=None, private_key=None, passphrase=None,
            escalation_type=None, escalation_username=None,
            escalation_password=None,
            description=None, group=None, visibility=None, users=None
    ):
        if public_key is not None:
            public_key = self._sc.file.name_or_upload(public_key)

        if private_key is not None:
            private_key = self._sc.file.name_or_upload(private_key)

        return self.edit(
            id, prefill, name, 'ssh', description, group, visibility, users,
            username=username, password=password,
            publicKey=public_key,
            privateKey=private_key, passphrase=passphrase,
            privilegeEscalation=escalation_type,
            escalationUsername=escalation_username,
            escalationPassword=escalation_password
        )

    def edit_windows(
            self, id, prefill=True, name=None,
            username=None, password=None, domain=None,
            description=None, group=None, visibility=None, users=None
    ):
        return self.edit(
            id, prefill, name, 'windows',
            description, group, visibility, users,
            username=username, password=password, domain=domain
        )

    def edit_snmp(
            self, id, prefill=True, name=None,
            community=None,
            description=None, group=None, visibility='user', users=None
    ):
        return self.edit(
            id, prefill, name, 'snmp',
            description, group, visibility, users,
            communityString=community
        )

    def edit_kerberos(
            self, id, prefill=True, name=None,
            ip=None, port=None, protocol=None, realm=None,
            description=None, group=None, visibility=None, users=None
    ):
        return self.edit(
            id, prefill, name, 'kerberos',
            description, group, visibility, users,
            ip=ip, port=port, protocol=protocol, realm=realm
        )

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

    def delete_simulate(self, *ids):
        return self._request('deleteSimulate', {
            'credentials': [{'id': id} for id in ids]
        })['effects']

    def delete(self, *ids):
        return self._request('delete', {
            'credentials': [{'id': id} for id in ids]
        })['credentials']
