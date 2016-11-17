import requests 
import ujson
from client_side.websocket import RTCWebSocketClient
from tornado import ioloop
from forgery_py import name as fgname

def dispatch():
    uid = fgname.full_name()
    response = requests.get('http://127.0.0.1:8888/api/join?uid=%s' % uid)




def main():
    #uid = raw_input("Please input your uid:")
    uid = fgname.full_name()
    response = requests.get('http://127.0.0.1:8888/api/join?uid=%s' % uid)
    """
    {
        "ip":"127.0.0.1",
        "port":9001,
        "node":1,
        "room":3
    }
    """
    data = response.content
    data = ujson.loads(data)
    if data == -1:
        print 'Currently no more node for use'
    else:
        ip = data['ip']
        port = data['port']
        node = data['node']
        room = data['room']
        print 'node[%s]---room[%s]' % (node, room) 
    
    io_loop = ioloop.IOLoop.instance()
    client = RTCWebSocketClient(io_loop)
    ws_url = "ws://127.0.0.1:9000/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip,port,node,room,uid)
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10, dispatch=dispatch)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    import threading
    import time
    for i in xrange(10):
        threading.Thread(target=dispatch, args=(), name='thread-' + str(i)).start()
        time.sleep(2)
