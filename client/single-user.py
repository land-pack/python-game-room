import requests 
import ujson
from client_side.websocket import RTCWebSocketClient
from tornado import ioloop


def dispatch(*args):
    print args



def main():
    uid = raw_input("Please input your uid:")
    response = requests.get('http://127.0.0.1:8888/api/join?uid=%s' % uid)
#   response = requests.get('http://192.168.50.12:8888/api/join?ck=%s' % uid)
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
    print data
    if str(100) == data.get("status"):
        data = data.get("body")
        ip = data['ip']
        port = data['port']
        node = data['node']
        room = data['room']
        print 'node[%s]---room[%s]' % (node, room) 

    
        io_loop = ioloop.IOLoop.instance()
        client = RTCWebSocketClient(io_loop)
# ws_url = "ws://192.168.50.12:9000/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip,port,node,room,uid)
#        ws_url = "ws://192.168.50.12:9000/vguess?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip,port,node,room,uid)
        ws_url = "ws://127.0.0.1:9000/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip,port,node,room,uid)
        
        client.connect(ws_url, auto_reconnet=True, reconnet_interval=10, dispatch=dispatch)

        try:
            io_loop.start()
        except KeyboardInterrupt:
            client.close()
    else:
        print 'no room or node avaible ..'


if __name__ == '__main__':
    main()
