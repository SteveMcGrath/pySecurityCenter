from .base import Module, extract_value


class Alert(Module):
	_name = "alert"

	@extract_value('alerts')
	def init(self):
		return self._request('init')
