import time


class TTLManager(object):
    """
    Set some thing during a time check it whether timeout!
    """
    _key_hash_time = {}

    def __init__(self):
        pass

    def update(self, key, timeout=5):
        self.timeout = timeout
        self._key_hash_time[key] = time.time()

    def is_expire(self, key):
        if time.time() > self._key_hash_time[key] + self.timeout:
            return True
        else:
            return False

    def remove_if_expire(self, key):
        if self.is_expire(key):
            del self._key_hash_time[key]
            return True
        return False


if __name__ == '__main__':
    ttl = TTLManager()
    ttl.update('jack')
    print ttl.is_expire('jack')
    time.sleep(3)
    print ttl.is_expire('jack')
    time.sleep(3)
    print ttl.is_expire('jack')
    print ttl._key_hash_time
    ttl.remove_if_expire('jack')
    print ttl._key_hash_time
