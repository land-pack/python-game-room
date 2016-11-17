import os
import json
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket
from tornado.options import options, define

#from lib.room import RoomManager
#from lib.core import DispatchCommand
#from lib.node import NodeManager
from data_server.room import RoomManager
from data_server.node import NodeManager
from data_server.views import dc

#dcommand = DispatchCommand()

#import data_server.views


define(name="port", default=8888, help="default port", type=int)
mmt = NodeManager()
manager = RoomManager(prefix='r_')
clients = []
client_handler_hash_connect = {}



class JoinHandler(web.RequestHandler):
    def get(self):
        """
        Usage:
            http://127.0.0.1:8880/api/join?uid=frank
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
        
        uid = self.get_argument("uid")
        room = manager.check_in(uid)
        response = mmt.landing(room, uid)
        if response == -1:
            # rollback ...
            manager.check_out(uid)
        #TODO let the delegate server know
        # try ..except should be here ...
        ip = response.get("ip")
        port = response.get("port")
        node = response.get("node")
        machine = "%s-%s" % (ip, port)
        client_handler = mmt._machine_hash_connect[machine]
        connect = client_handler_hash_connect[client_handler]
        connect.write_message(ujson.dumps({"uid":uid, "room":room, "node":node}))
        self.write(ujson.dumps(response))


class MonitorHandler(web.RequestHandler):
    def get(self):
        mmt.status()
        manager.status()
        self.write("ok")


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
        client_handler_hash_connect[id(self)] = self
        response = {"node_id":node_id}
        #request = {"command":"connect","ip":ip, "port": port}
        #request = ujson.dumps(response)
        #response = dc.render(request, mmt)
        response = {"command":"connect", "status":"success"}
        self.write_message(ujson.dumps(response))


    def on_close(self):
        mmt.unregister(self)
        clients.remove(self)
        del client_handler_hash_connect[id(self)]


    def on_message(self, msg):
        response = dc.render(msg, mmt, manager=manager)
        if response:
            self.write_message(response)


if __name__ == '__main__':
    #import data_server.views
    options.parse_command_line()
    application = web.Application([
	    (r'/ws', WebSocketHandler),
	    (r'/api/join', JoinHandler),
            (r'/monitor', MonitorHandler)
	],
    debug=True)
    print 'Listen on ', options.port
    application.listen(options.port)
    ioloop.IOLoop.instance().start()
