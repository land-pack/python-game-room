import ujson
from utils import set_expire


class BaseMachineHashNodeManager(object):
    """
    @property _machine_hash_node
    Example:
            {
                '127.0.0.1-9001':0,
                '127.0.0.1-9002':1,
                '127.0.0.1-9003':2,
            }
    """
    _machine_hash_node = {}
    """
    @property _node_hash_machine
    Example:
            {
                0: '127.0.0.1-9001'
                1: '127.0.0.1-9002'
                2: '127.0.0.1-9003'
            }
    """
    _node_hash_machine = {}

    """
    @property _node_hash_room
    Examle:
            {
                0: ['room1', 'room2', ...],
                1: ['room11', 'room12', ...],
                2: ['room21', 'room22', ...],
            }
    """
    _node_hash_room = {}
    """
    @property _connect_hash_machine
    Example:
            {
                4388089088:'127.0.0.1-9001',
                4388089089:'127.0.0.1-9002',
                4388089090:'127.0.0.1-9003',
            }
    """
    _connect_hash_machine = {}
    """
    @property _machine_hash_connect
    Example:
            {
               '127.0.0.1-9001': 4388089088,
               '127.0.0.1-9001': 4388089089,
               '127.0.0.1-9001': 4388089090,
            }
    """
    _machine_hash_connect = {}
    """
    @property _machine_hash_handler
    The handler is a object of websocket connect
    you can do the send/recv operations!
    """
    _machine_hash_handler = {}
    """
    @property _node_hash_counter
    The counter of room in the node!
    After a new room append to this node
    this property will auto increment!
    Example:
            { 0 : 64 }
            { 1 : 64 }
            { 2 : 32 }
            { 3 : 0  }
            { 4 : 0  }
    """

    _node_hash_counter = {}

    """
    @property _node_index:
    Auto increment
    """
    _node_index = 0

    """
    @property _node_max_size
    When you use this class, you should configure it!
    default value are given!
    """
    _node_max_size = 32
    """
    @property _node_max_user_number
    One node can hold the number of user!
    default value are given! assume if each room
    can hold 10 user! so we have 320 on each node!
    """
    _node_max_user_number = 320

    def register(self, connect, ip, port, node=None):
        """
        @param ip: proxy server ip
        @param port: proxy server port
        @param node: -1 --> normaly, 0+ --> recovery
        @return: None
        """
        node = int(node)
        if node == -1:
            node_id = self._node_index
        else:
            node_id = node
        key = "%s-%s" % (ip, port)
        if key in self._machine_hash_connect:
            """
            This node has already register to the server
            so ignore this register instead mark it as alive!
            """
            self._connect_hash_machine[id(connect)] = key  # recreate ...
            self._machine_hash_connect[key] = id(connect)  # update ...
            self._machine_hash_handler[key] = connect  # update
            node_id = self._machine_hash_node[key]
            return node_id

        else:
            """
            This node is first time come to the server
            so register as new one!
            """
            self._machine_hash_node[key] = node_id
            self._node_hash_room[node_id] = []
            self._connect_hash_machine[id(connect)] = key
            self._machine_hash_connect[key] = id(connect)
            self._machine_hash_handler[key] = connect
            self._node_hash_machine[node_id] = key
            self._node_hash_counter[node_id] = 0  # 0 room number!
            self._node_hash_user[node_id] = 0  # 0 user number!
            if node == -1:
                self._node_index = self._node_index + 1
            return node_id

    def unregister(self, connect):
        """
        @param connect: websocket connect
        if websocket disconnect, we will remove this item
        from self._machine_hash_connect & self._connect_hash_machine!
        after do this, we actully mark it as un-live! but it's
        still store on the memory so, next time it come back
        still got the same node name!
        Example:
            [Node123] -----> [127.0.0.1:90001]
                ....disconnect....
                ....reconnect..... 
            [Node123] -----> [127.0.0.1:90001]
        """
        del self._connect_hash_machine[id(connect)]

    def recovery_node(self, data):
        """
        @param data: a dict-type
        Example:
                {
                    "command": "ack_recovery",      # command
                    'node': 2,                      # Node id
                    'user': 18,                     # user number
                    'rooms': [r1, r2, r3]           # room set
                    'counter': 64,                  # the total room in node
                    'machine':'127.0.0.1-9001'      # machine id
                }
        """
        node = data.get("node")
        user = data.get("user")
        rooms = data.get("rooms")
        counter = data.get("counter")
        machine = data.get("machine")

        self._node_hash_user[node] = user
        self._node_hash_counter[node] = counter
        for room in rooms:
            self._room_hash_node[room] = node


class NodeManager(BaseMachineHashNodeManager):
    """
    @property _user_hash_node
    Example:
            { u1 : 0,
              u2 : 0,
              u3 : 1 
            }
    """
    _user_hash_node = {}
    """
    @property _room_hash_node
    Example:
            { 0 : 0,
              1 : 0,
              2 : 1 
            }
    """
    _room_hash_node = {}
    """
    @property _node_hash_user
    Example:
            { 0 : 32 }
            { 1 : 9  }
            { 2 : 2  }
    """
    _node_hash_user = {}

    def is_running(self, node):
        """
        @param node: node id
        @return: Boolean, true if the node running okay!
        else false return !
        """
        if node in self._node_hash_machine:
            machine = self._node_hash_machine[node]
            if machine in self._machine_hash_connect:
                return True
        return False

    def is_user_fillout_node(self, node):
        """
        @param node: node id
        @return : Boolean, true if the node has seat available
        else return False!
        """
        current_user_number = self._node_hash_user.get(node, 0)
        if current_user_number < self._node_max_user_number:
            return False
        else:
            return True

    def landing(self, room, uid):
        """
        @param room: room id
        @param uid: user id
        @return : node id, if no more node for use! return -1
        Usage:
            mmt.install_room(room, user)
        Example:
            {
                "ip": "127.0.0.1",
                "port":9001,
                "node":1,
                "room":2
            }
        """

        if room in self._room_hash_node:
            """
            if the target room has been install on some one node
            just search that node, return it!
            """
            node = self._room_hash_node[room]
            ip, port = self._node_hash_machine[node].split('-')
            self._user_hash_node[uid] = node
            self._node_hash_user[node] = self._node_hash_user[node] + 1
            response = {"ip": ip, "port": port,
                        "node": node, "room": room, "uid": uid}
            return response

        for node in self._node_hash_counter:
            if self.is_user_fillout_node(node):
                return -1
            else:

                self._room_hash_node[room] = node
                self._node_hash_room[node].append(room)
                self._node_hash_counter[node] = self._node_hash_counter[node] + 1
                self._node_hash_user[node] = self._node_hash_user[node] + 1
                ip, port = self._node_hash_machine[node].split('-')
                self._user_hash_node[uid] = node
                response = {"ip": ip, "port": port,
                            "node": node, "room": room}
                return response

    def flying(self, uid):
        node = self._user_hash_node[uid]
        self._node_hash_user[node] = self._node_hash_user[node] - 1

    def notify(self, response):
        """
        if a new user has come in, the room server will send
        a message to let that node know! someone coming soon!

        Args:
            response:

        Returns:

        """
        ip = response.get("ip")
        port = response.get("port")
        node = response.get("node")
        uid = response.get("uid")
        room = response.get("room")
        machine_name = "%s-%s" % (ip, port)
        websocket_handler = self._machine_hash_handler[machine_name]
        websocket_handler.write_message(ujson.dumps({"command": "check_in", "uid": uid, "room": room, "node": node}))
        set_expire(uid)

    def node_status(self):
        print '+' * 50
        print"_machine_hash_connect", self._machine_hash_connect
        print"_connect_hash_machine", self._connect_hash_machine
        print"_machine_hash_node", self._machine_hash_node
        print"_node_hash_room", self._node_hash_room
        print"_room_hash_node", self._room_hash_node
        print"_node_hash_counter", self._node_hash_counter
        print"_node_hash_user", self._node_hash_user
        print '+' * 50


if __name__ == '__main__':
    #   mmt = NodeManager()
    #    mmt.register('connect1', '127.0.0.1','9001')
    #    mmt.register('connect2', '127.0.0.1','9002')
    #    print mmt._machine_hash_connect
    #    print mmt._connect_hash_machine
    #    print mmt._machine_hash_node
    #    print mmt._node_hash_room
    #    print mmt._room_hash_node
    #    print 'test unregister'
    #    mmt.unregister('connect2')
    #    mmt.register('connect2a', '127.0.0.1','9002')
    #    print mmt._node_hash_room
    # =====================recovery test
    empty = NodeManager()
    empty.register('connect1', '127.0.0.1', '9002', node=2)
    # empty.recovery_connect('connect1a', '127.0.0.1','9002')
    sample_data = {
        'node': 2,  # Node id
        'user': 18,  # user number
        'rooms': ['r1', 'r2', 'r3'],  # room set
        'counter': 8,  # the total room in node
        'machine': '127.0.0.1-9002'  # machine id
    }
    empty.recovery_node(sample_data)
    empty.node_status()
