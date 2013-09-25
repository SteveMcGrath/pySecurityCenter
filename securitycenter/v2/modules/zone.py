from .base import Module, extract_value


class Zone(Module):
    _name = 'zone'

    @extract_value('zones')
    def init(self):
        return self._request('init')

    def add(self):
    	#TODO add
    	raise NotImplementedError

	def edit(self):
		#TODO edit
		raise NotImplementedError

	def delete(self, *ids):
		return self._request('delete',{
			'zones': [{'id':id} for id in ids]
		})