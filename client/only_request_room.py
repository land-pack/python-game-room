import requests 
import ujson
import threading
import time
from forgery_py import name as fgname


def join_request():
    uid = fgname.full_name()
    response = requests.get('http://127.0.0.1:8888/api/join?uid=%s' % uid)


if __name__ == '__main__':

    for i in xrange(20):
        threading.Thread(target=join_request, args=(), name='thread-' + str(i)).start()
        time.sleep(1)
