import logging
import time
import redis
import ujson

logger = logging.getLogger("cserver")

r = redis.Redis(host='127.0.0.1', port=6379)

REDIS_PREFIX = "CSERVER_PREFIX_"


def rename(key):
    return REDIS_PREFIX + key


def set_expire(key, ex=10):
    key = rename(key)
    if isinstance(key, dict):
        str_key = ujson.dumps(key)
        r.set(str_key, 1, ex=ex)
    else:
        r.set(key, 1, ex=ex)


def is_expire(key):
    key = rename(key)
    if isinstance(key, dict):
        key = ujson.dumps(key)
    value = r.get(key)
    if value == None:
        return True
    value = int(value)
    if value == 0:
        return True
    else:
        return False


def mark_connected(key):
    if isinstance(key, dict):
        str_key = ujson.dumps(key)
        r.delete(str_key)
    else:
        r.delete(key)


def check_expire(manager):
    remove_list = []
    for uid in manager._user_pending_status_set:
        if is_expire(uid):
            logger.warning("User [%s] has expired" % uid)
            manager.check_out(uid)
            remove_list.append(uid)

    for uid in remove_list:
        remove_list.remove(uid)
        manager._user_pending_status_set.remove(uid)


if __name__ == '__main__':
    key = {"node": 1, "room": 2}
    key = 'hello jack'
    set_expire(key)
    print is_expire(key)
    time.sleep(3)
    mark_connected(key)
    print is_expire(key)
    mark_connected(key)
    time.sleep(3)
    print is_expire(key)
