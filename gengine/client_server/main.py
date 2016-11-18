import socket
from tornado import ioloop
from websocket import RTCWebSocketClient

def run(cport=8888, port=9001, dc=None):
    host=socket.gethostname()
    ip=socket.gethostbyname(host)
    ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s' % (cport, ip, port)
    websocket_client = RTCWebSocketClient()
    websocket_client.connect(ws_url, dispatch=dc.dispatch, auto_reconnet=True, reconnet_interval=10)
    io_loop = ioloop.IOLoop.instance()
    token = RTCWebSocketClient(io_loop)
    return io_loop, websocket_client 
