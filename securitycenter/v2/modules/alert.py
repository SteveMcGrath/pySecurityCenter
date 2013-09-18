from .base import Module, extract_value


class Alert(Module):
	_name = "alert"

	@extract_value('alerts')
	def init(self):
		return self._request('init')

	def edit(self):
		#TODO asset::edit
+        raise NotImplementedError 

	def delete(self):
		#TODO asset::edit
+        raise NotImplementedError 

	def execute(self):
		#TODO asset::edit
+        raise NotImplementedError 

	def query(self):
		#TODO asset::edit
+        raise NotImplementedError 

	def validateAdd(self):
		#TODO asset::edit
+        raise NotImplementedError 

	def validateEdit(self):
		#TODO asset::edit
+        raise NotImplementedError 
