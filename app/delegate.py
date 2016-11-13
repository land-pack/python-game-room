import socket
import ujson
from lib.websocket import RTCWebSocketClient
from tornado import ioloop
from tornado import websocket
from tornado import web
from tornado.options import options, define
#from core import make_redirect
from lib.room import RoomManager

define(name="port", default=9001, help="default port", type=int)
define(name="cport", default=8888, help="default port", type=int)
clients = []
manager = RoomManager()

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
    message = websocket_client.message
    print message 
    _node_id = 0 #ujson.loads(message).get("node")
    room_list = set()


    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        Usage: The argument with url only for `nginx` identify it!
        Example:
            url="ws://127.0.0.1:8880/ws?ip=%s&port=%s&node=%s&user=%s" % (ip, port, node, user)
            ws = websocket.WebSocketApp(url)
        """
        #node = self.get_argument("node")
        #user = self.get_argument("user")
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
        data = ujson.loads(msg)
        user= data.get("user")
        room = manager.check_in(user)
        if room in self.room_list:
            pass
        else:
            self.room_list.add(room)
            req = {"command":"update_room_counter",
                    "node":self._node_id,
                    "room_counter":len(self.room_list)}
            websocket_client.send(req)
        response = ujson.dumps({"room":room})
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
