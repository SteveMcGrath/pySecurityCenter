from .base import Module, extract_value


class Alert(Module):
	_name = "alert"

	@extract_value('alerts')
	def init(self):
		"""Returns a list of all alerts and their metadata
.

		"""
		return self._request('init')

	def edit(self):
		#TODO asset::edit
		raise NotImplementedError 

	def delete(self, owner, *ids):
		return self._request('delete', {
			'alerts': [{'id': id} for id in ids}],
			'ownerID': owner
			}) ['alerts']

	def execute(self, id):
		return self._request('execute', {
			'id': id
			}) 

	def query(self):
		#TODO asset::query
		raise NotImplementedError 

	def validateAdd(self):
		#TODO asset::validateAdd
		raise NotImplementedError 

	def validateEdit(self):
		#TODO asset::validateEdit
		raise NotImplementedError 
