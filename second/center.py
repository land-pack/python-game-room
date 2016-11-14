import os
import json
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket
from tornado.options import options, define
from lib.room import RoomManager
from lib.core import make_response
from lib.node import NodeManager
from lib.room import RoomManager

define(name="port", default=8888, help="default port", type=int)
mmt = NodeManager()
manager = RoomManager()
clients = []



class JoinHandler(web.RequestHandler):
    def get(self):
        """
        Usage:
            http://127.0.0.1:8880/api/join?user=frank
        Desc:
            system will check MachineManagerTable to
            get the currently node for response the client!
            [User] ---http-----------> [Area] --------------
                                       {... }             ]
            token  <-----http------- MachineManagerTable ---

            [User] ---websocket ------>[Node] --------->[Area]

        Example:
        response={
                "ip": "127.0.0.1",
                "port": "9001",
                "node": "2",
                "room": "1",
            }
        """
        
        user = self.get_argument("user")
        room = manager.check_in(user)
        response = mmt.install_room(room, user)
        if response == -1:
            manager.check_out(user)
        self.write(ujson.dumps(response))


class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        Usage:
            ws = websocket.WebSocketApp("ws://127.0.0.1:8888/ws?ip=%s&port=%s" % (ip, port)
        Desc:
            [Node] ----------------> [Area] --------
                                                    ]
            [Node] <--------------------------------
        """
        ip = self.get_argument('ip')
        port = self.get_argument("port")
        node_id = mmt.register(self, ip, port)
        clients.append(self)
        response = {"node_id":node_id}
        self.write_message(ujson.dumps(response))


    def on_close(self):
        mmt.unregister(self)
        clients.remove(self)


    def on_message(self, msg):
        response = make_response(msg, mmt)
        self.write_message(response)


if __name__ == '__main__':
    options.parse_command_line()
    application = web.Application([
	    (r'/ws', WebSocketHandler),
	    (r'/api/join', JoinHandler),
	],
    debug=True)
    print 'Listen on ', options.port
    application.listen(options.port)
    ioloop.IOLoop.instance().start()
