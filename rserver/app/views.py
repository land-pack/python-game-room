import os
import json
import datetime
import logging
import logging.config
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket

from lib.room import RoomManager
from lib.node import NodeManager
from lib.utils import set_expire, is_expire
from lib.views import dc
from lib.utils import check_expire



logger = logging.getLogger("rserver")



mmt = NodeManager()
manager = RoomManager(prefix='')
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
        print 'landing response', response
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
        set_expire(uid)
        self.write(ujson.dumps(response))


class DashHandler(web.RequestHandler):
    def get(self):
        """
        manager.node.room.user,
        """
        output = ''
        lines = []
        tag = "id,value"
        lines.append(tag)
        root = "Manager"
        lines.append(root)
        for node in mmt._node_hash_room:
            rooms = mmt._node_hash_room[node]
            root2 = 'Manager.node_%s' % node
            lines.append(root2)
            for room in rooms:
                root3 = 'Manager.node_%s.room_%s' % (node, room)
                lines.append(root3)
                uids = manager._room_hash_user_set[room]
                for uid in uids:
                    output='Manager.node_%s.room_%s.uid_%s' % (node, room, uid)
                    lines.append(output)
        with open("./app/templates/data.csv", "w+") as fd:
            for line in lines:
                fd.write(line)
                fd.write("\n")
        self.render("dash.html")


class CSVHandler(web.RequestHandler):
    def get(self):
        self.render("data.csv")


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
        @param ip: node server ip
        @param port: node server port
        @param mode: the server connect mode
        'normally' will given if the machine is first time connect!
        'recovery' will given if the machine try to reconnect room server!
        to help room-server remeber something which its missing during some
        die~~
        
        Usage:
            ws = websocket.WebSocketApp("ws://127.0.0.1:8888/ws?ip=%s&port=%s&mode=%s" % (ip, port, mode)
        Desc:
            [Node] ----------------> [Area] --------
                                                    ]
            [Node] <--------------------------------
        """
        mode = self.get_argument('mode')
        logger.warning('current mode [%s]' %  mode)
        ip = self.get_argument('ip')
        port = self.get_argument("port")
        clients.append(self)
        client_handler_hash_connect[id(self)] = self
        logger.warning("The mode is [%s]" % mode)
        mode = int(mode)
        if mode == -1:
        # Normally mode
            node_id = mmt.register(self, ip, port, mode=mode)
            logger.warning("The node is is [%s]" % node_id)
            response = {"command":"connect", "status":"ok", "mode":"normally","node":node_id}
            self.write_message(ujson.dumps(response))
        else:
            logger.warning("Recovery data ....")
            node_id = mmt.register(self, ip, port, mode=mode)
            response = {"command":"connect", "status":"ok", "mode":"recovery"}
            self.write_message(ujson.dumps(response))



    def on_close(self):
        mmt.unregister(self)
        clients.remove(self)
        del client_handler_hash_connect[id(self)]


    def on_message(self, msg):
        logger.info('[Recv] %s' % msg)
        response = dc.render(msg, mmt, manager=manager)
        if response:
            self.write_message(response)
