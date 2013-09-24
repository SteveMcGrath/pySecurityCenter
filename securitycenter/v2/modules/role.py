from .base import Module, extract_value


class Role(Module):
    _name = 'role'

    @extract_value('roles')
    def init(self):
        return self._request('init')


    def add(self):
    	#TODO role::add
        raise NotImplementedError


	def edit(self):
		#TODO role::edit
        raise NotImplementedError


	def delete(self, *ids):
		return self._request('delete',{
			'roles': [{'id': id} for id in ids]
			}) ['roles']
