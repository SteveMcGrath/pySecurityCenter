from .base import Module


class Daemons(Module):
    _name = 'daemons'

    def init(self):
        return self._request('init')

    def start_all(self):
        return self._request('startAll')

    def stop_all(self):
        return self._request('stopAll')

    def restart_all(self):
        return self._request('restartAll')

    def stop(self):
        #TODO daemon:stop
        raise NotImplementedError

    def start(self):
        #TODO daemon:start
        raise NotImplementedError

    def restart(self):
        #TODO daemon:restart
        raise NotImplementedError