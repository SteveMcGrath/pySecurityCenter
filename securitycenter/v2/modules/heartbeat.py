from base import *

class Heartbeat(Module):
    _name = "heartbeat"

    def init(self):
        return self._request("init")

    def beat(self, module=None, module_params=None, messages_viewed=None, messages_deleted=None, id=None):
        if messages_viewed is None:
            messages_viewed = []

        if messages_deleted is None:
            messages_deleted = []

        return self._request("beat", {
            "messagesViewed": [{"id": int(m_id)} for m_id in messages_viewed],
            "messagesDeleted": [{"id": int(m_id)} for m_id in messages_deleted],
            "module": module,
            "moduleParams": module_params,
            "id": id
        })