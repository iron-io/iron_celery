from iron_cache import IronCache
from celery.backends.base import KeyValueStoreBackend
from kombu.utils.url import _parse_url

class IronCacheBackend(KeyValueStoreBackend):
    _client = None
    _host = None
    _project_id = None
    _token = None
    _ncache = None

    def __init__(self, url = None, *args, **kwargs):
        super(IronCacheBackend, self).__init__(*args, **kwargs)

        _, self._host, _, self._project_id, self._token, self._ncache, _ = _parse_url(url)

        if self._ncache == None:
            self._ncache = "Celery" 

    @property
    def client(self):
        if self._client is None:
            self._client = IronCache(project_id = self._project_id, token = self._token, host = self._host)

        return self._client

    def set(self, key, value):
        self.client.put(cache = self._ncache, key = key, value = value.encode("base64"))

    def get(self, key):
        try:
            return self.client.get(cache = self._ncache, key = key).value.decode("base64")
        except:
            pass

        return None

    def delete(self, key):
        self.client.delete(cache = self._ncache, key = key)
