import socket
from lib.websocket import RTCWebSocketClient
from tornado import ioloop
from tornado import websocket
from tornado import web
from tornado.options import options, define
#from core import make_redirect
#from lib.room import NodeManager

define(name="port", default=9001, help="default port", type=int)
define(name="cport", default=8888, help="default port", type=int)
clients = []
#manager = RoomManager()

io_loop = ioloop.IOLoop.instance()
token = RTCWebSocketClient(io_loop)


options.parse_command_line()
host=socket.gethostname()
ip=socket.gethostbyname(host)
cport = options.cport
ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s' % (cport, ip, options.port)
websocket_client = RTCWebSocketClient()
websocket_client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)
"""
    Delegate Server ----------WebSocket-------> Area Server
"""

class DelegateWebSocketHandler(websocket.WebSocketHandler):
    """
    This websocket server orient to client-side!
    client A --------------               ----- Delegate Server A
                           } nginx ---> {
    client B --------------               ----- Delegate Server B
    """
    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        Usage:
        Example:
            url="ws://127.0.0.1:8880/ws?ip=%s&port=%s&node=%s&room=%s&user=%s" % (ip, port, node, room, user)
            ws = websocket.WebSocketApp(url)
        """
        ip = self.get_argument("ip")
        port = self.get_argument("port")
        node = self.get_argument("node")
        room = self.get_argument("room")
        user = self.get_argument("user")
        print 'client request has come in with '
        print 'node',node
        print 'room',room
        print 'user',user

        #TODO ......
        #clients[id(self)] = "anonymous"
        clients.append(self)

    def on_close(self):
        """
        If someone leave out, will send heartbeat/ if time out after servaral try
        will notifiy the area-server! and if the area-server has acknowledge this operation
        and then this user will remove from local processs memory!
        Example:
            if acknowledge == True:
                local_hash.remove(some_one)
            else:
                wait.. 
        """
        clients.remove(self)
        #user = clients[id(self)]
        #msg = {"command": "check_out", "user": user}
        #make_redirect(msg, token)
        # log.this user, if timeout ,will notify boss server


    def on_message(self, msg):
        #response = make_redirect(msg, token)
        response = 'hello ...'
        self.write_message(response)


def main():
    application = web.Application([
        (r'/ws', DelegateWebSocketHandler),
        ],
        debug=True)
    application.listen(options.port)


    try:
        io_loop.start()
    except KeyboardInterrupt:
        websocket_client.close()


if __name__ == '__main__':
    main()
