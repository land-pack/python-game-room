import os
import json
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket
from tornado.options import options, define
from lib.room import RoomManager
from lib.core import make_response
from lib.db import MachineManagerTable


define(name="port", default=9000, help="default port", type=int)
manager = RoomManager()
mmt = MachineManagerTable()

clients = []
delegate_clients = {}


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
            response
            {
                "host": "127.0.0.1",
                "port": "9001",
                "node": "2",
                "room": "room1"
            }
            data = ujson.dumps(response)
        """
        
        user = self.get_argument("user")
        data = mmt.dispatch(user)   #TODO ...
        self.write(data)


class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        Usage:
            ws = websocket.WebSocketApp("ws://127.0.0.1:8880/ws?ip=%s&port=%s" % (ip, port)
        Desc:
            [Node] ----------------> [Area] --------
                                                    ]
            [Node] <--------------------------------
        """
        ip = self.get_argument('ip')
        port = self.get_argument("port")
        mmt.register(self, ip, port)
        clients.append(self)


    def on_close(self):
        mmt.unregister(self)
        clients.remove(self)


    def on_message(self, msg):
        response = make_response(msg, manager)
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
