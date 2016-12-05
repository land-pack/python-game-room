import logging.config
import ujson
from tornado import web
from tornado import websocket
from control import rs

logger = logging.getLogger("rserver")

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

        data = {}
        uid = self.get_argument("uid")
        room = rs.check_in(uid)
        response = rs.landing(room, uid)
        if response == -1:
            # rollback ...
            rs.check_out(uid)
            self.write({"command": "bad", "info": "No more seat!"})
        else:
            data["body"] = response
            data["status"] = "100"
            self.write(ujson.dumps(data))
            rs.notify(response)


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
        for node in rs._node_hash_room:
            rooms = rs._node_hash_room[node]
            root2 = 'Manager.node_%s' % node
            lines.append(root2)
            for room in rooms:
                root3 = 'Manager.node_%s.room_%s' % (node, room)
                lines.append(root3)
                uids = rs._room_hash_user_set[room]
                for uid in uids:
                    output = 'Manager.node_%s.room_%s.uid_%s' % (node, room, uid)
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
        rs.node_status()
        rs.room_status()
        self.write("ok")


class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        """
        @param ip: node server ip
        @param port: node server port
        @param node: the server connect node
        'normally' will given if the machine is first time connect!
        'recovery' will given if the machine try to reconnect room server!
        to help room-server remeber something which its missing during some
        die~~
        
        Usage:
            ws = websocket.WebSocketApp("ws://127.0.0.1:8888/ws?ip=%s&port=%s&node=%s" % (ip, port, node)
        Desc:
            [Node] ----------------> [Area] --------
                                                    ]
            [Node] <--------------------------------
        """
        node = self.get_argument('node')
        node = int(node)
        logger.warning('Current Node [%s]' % node)
        ip = self.get_argument('ip')
        port = self.get_argument("port")
        machine = "%s-%s" % (ip, port)
        clients.append(self)
        client_handler_hash_connect[id(self)] = self

        if node == -1:
            # Normally node
            node_id = rs.register(self, ip, port, node=node)
            logger.warning("Register success! with node [%s]" % node_id)
            response = {"command": "connect", "status": "ok", "node": node_id, "machine": machine}
            self.write_message(ujson.dumps(response))
        else:
            logger.warning("Recovery node data ....")
            rs.register(self, ip, port, node=node)
            response = {"command": "recovery", "status": "ok"}
            self.write_message(ujson.dumps(response))

    def on_close(self):
        rs.unregister(self)
        clients.remove(self)
        del client_handler_hash_connect[id(self)]

    def on_message(self, msg):
        logger.info('[Recv] from client server: %s' % msg)
        response = rs.render(msg)
        if response:
            self.write_message(response)
