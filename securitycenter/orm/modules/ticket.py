from .base import Module, extract_value


class Ticket(Module):
    _name = 'ticket'

    @extract_value('tickets')
    def init(self):
        return self._request('init')

    def add(self):
        #TODO ticket:add
        raise NotImplementedError

    def edit(self):
        #TODO ticket:edit
        raise NotImplementedError

    def edit_status(self):
        #TODO ticket:editStatus
        raise NotImplementedError

    def purge(self):
        #TODO ticket:purge
        raise NotImplementedError

    def delete(self):
        #TODO ticket:delete
        raise NotImplementedError

    def query(self):
        #TODO ticket:query
        raise NotImplementedError

    def validate_add(self):
        #TODO ticket:validateAdd
        raise NotImplementedError

    def validate_edit(self):
        #TODO ticket:edit
        raise NotImplementedError