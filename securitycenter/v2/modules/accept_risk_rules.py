from .base import Module, extract_value


class AcceptRiskRules(Module):
    _name = "accept_risk_rules"

    def init(self):
        return self._request('init')

    def get_rules(self, rep, plugin, port):
        """Returns risk rules

        :param rep: repID
        :param plugin: pluginID
        :param port: port number

        :return: returns risk rules

        """
        return self._request('getRules', {
            'repId': rep,
            'pluginID': plugin,
            'port': port
        })

    def add(self):
        #TODO: add
        raise NotImplementedError

    def delete(self, rules):
        """Deletes risk rules

        :param rules: acceptRiskRules

        :return
        """

        return self._request('delete', {
            'acceptRiskRules': rules
        })

    def apply(self, rep):
        """Applies specified changes to risk rules

        :param rep: redID

        :return: params
        """

        return self._request('apply', {
            'repID': rep
        })