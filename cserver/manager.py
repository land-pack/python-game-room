import socket
import os
import ujson
import logging
import logging.config
from tornado import ioloop
from tornado import websocket
from tornado import web
from tornado.options import options, define
from app.views import local_system
from app import color


logging.config.fileConfig("log.conf")
logger = logging.getLogger("cserver")

define(name="port", default=9001, help="default port", type=int)
define(name="cport", default=8888, help="default port", type=int)


g_client_connect = []
g_connect_hash_uid = {}


"""
You have `local_system` , so you have it all!
==================================================
local_system.check_in(connect, room, uid)
local_system.check_out(connect=None, timeout=15)
local_system.kick_off(uid)
==================================================
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
        local_system.check_in(self, room, uid)

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
        response = local_system.check_out(self)
        g_client_connect.remove(self)
        del g_connect_hash_uid[id(self)]



    def on_message(self, msg):
        data = local_system.parser(msg)
        response = local_system.check_in(data)
        if response:
            self.write_message(response)


def main():
    application = web.Application([
        (r'/ws', DelegateWebSocketHandler),
        ],
        debug=True)
    options.parse_command_line()
    application.listen(options.port)
    io_loop = ioloop.IOLoop.current()
    local_system.run(port=options.port)
    io_loop.start()


if __name__ == '__main__':
    main()
