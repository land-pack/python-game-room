import socket
import ujson
from client_server.websocket import RTCWebSocketClient
from tornado import ioloop
from tornado import websocket
from tornado import web
from tornado.options import options, define
from client_server.views import dc # to trigger the DispatchCommand 
from client_server.chat import tm
from client_server.local import LocalManager 
from client_server.chat import TalkManager

define(name="port", default=9001, help="default port", type=int)
define(name="cport", default=8888, help="default port", type=int)



g_client_connect = []
g_connect_hash_uid = {}


io_loop = ioloop.IOLoop.instance()
token = RTCWebSocketClient(io_loop)
options.parse_command_line()


host=socket.gethostname()
ip=socket.gethostbyname(host)
cport = options.cport
ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s' % (cport, ip, options.port)
websocket_client = RTCWebSocketClient()
websocket_client.connect(ws_url, dispatch=dc.dispatch, auto_reconnet=True, reconnet_interval=10)


lm = LocalManager()
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

    _connect_hash_uid = {}


    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        Usage: The argument with url only for `nginx` identify it!
        Example:
            url="ws://127.0.0.1:8880/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip, port, node, room, uid)
            ws = websocket.WebSocketApp(url)
        """
        uid = self.get_argument("uid")
        room = self.get_argument("room")
        response = lm.check_in(self, room, uid)
        g_client_connect.append(self)
        g_connect_hash_uid[id(self)]=uid
        #self._node_id = websocket_client.node_id
        websocket_client.send(response)


    def on_close(self):
        """
        If someone leave out, will send heartbeat/ if time out after servaral try
        will notifiy the area-server! and if the area-server has acknowledge this operation
        and then this uid will remove from local processs memory!
        Example:
            if acknowledge == True:
                local_hash.remove(some_one)
            else:
                wait.. 
        """
        response = lm.check_out(self)
        g_client_connect.remove(self)
        del g_connect_hash_uid[id(self)]
        #uid = clients[id(self)]
        #msg = {"command": "check_out", "uid": uid}
        #make_redirect(msg, token)
        # log.this uid, if timeout ,will notify boss server
        #req = {"command":"del_uid",
        #        #"node":self._node_id,
        #        "uid":g_connect_hash_uid[id(self)]
        #    }

        websocket_client.send(response)



    def on_message(self, msg):
        #data = ujson.loads(msg)
        #uid= data.get("uid")
        #    websocket_client.send(req)
        #response = ujson.dumps({"command":"in"})
        #tm.render(msg)
        #self.write_message(response)
        response = tm.render(msg, lm)
        if response:
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
