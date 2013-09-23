from .base import Module, extract_value


class AcceptRiskRules(Module):
	_name = "acccept_risk_rules"

	def init(self):
		return self._request('init')