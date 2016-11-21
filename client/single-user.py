import requests 
import ujson
from client_side.websocket import RTCWebSocketClient
from tornado import ioloop


def dispatch(*args):
    print args



def main():
    uid = raw_input("Please input your uid:")
    response = requests.get('http://127.0.0.1:8888/vroom/join?uid=%s' % uid)
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
    main()
