import socket
import time
from tornado import ioloop
from websocket import RTCWebSocketClient



def run(cport=8888, port=9001, dc=None, mode=None, lm=None):
    host=socket.gethostname()
    ip=socket.gethostbyname(host)
    ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s&mode=%s' % (cport, ip, port, 'normally')
    ws_recovery_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s&mode=%s' % (cport, ip, port, 'recovery')
    websocket_client = RTCWebSocketClient()
    websocket_client.connect(ws_url, ws_recovery_url, dispatch=dc.dispatch, auto_reconnet=True, reconnet_interval=10)
    io_loop = ioloop.IOLoop.instance()
    token = RTCWebSocketClient(io_loop)
    return io_loop, websocket_client 

