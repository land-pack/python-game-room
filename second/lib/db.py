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
    @property _node_index:
    Auto increment
    """
    _node_index = 0
    """
    @property _node_max_size
    The max number can live on one node!
    """
    _node_max_size = 50


    def __init__(self):
        pass


    def register(self, connect, ip, port):
        """
        @param ip: proxy server ip
        @param port: proxy server port
        @return: None
        """
        key = "%s-%s" % (ip, port)
        if key in self._machine_hash_connect:
            """
            This node has already register to the server
            so ignore this register instead mark it as alive!
            """
            self._connect_hash_machine[id(connect)] = key   # recreate ...
            self._machine_hash_connect[key] = id(connect)   # update ...
        else:
            """
            This node is first time come to the server
            so register as new one!
            """

            self._machine_hash_node[key] = self._node_index
            self._node_hash_room[self._node_index] = []
            self._node_index = self._node_index + 1
            self._connect_hash_machine[id(connect)] = key
            self._machine_hash_connect[key] = id(connect)
    
    
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
        #key = self._connect_hash_machine[id(connect)]
        #del self._machine_hash_connect[key]
        del self._connect_hash_machine[id(connect)]


class NodeManager(BaseMachineHashNodeManager):
    _room_max_size = 4
    _node_room = {}
 
    def is_die(self, connect):
        """
        @param connect: the websocket fd
        @return : True / False
        """
        if id(connect) in self._connect_hash_machine:
            return False
        else:
            return True

    
    def is_full(self, node):
        """
        @param node: number!
        @return : Boolean
        """
        rooms = self._node_hash_room[node]
        if rooms > self._node_max_size:
            return True
        else:
            return False

    
    def recovery(self, ):
        pass


    def in_node(self, node, rooms):
        """
        Example:
            rooms = {
                'room1': [ u1, u2, u3 ]
                'room2': [ u4, u5, u6 ]
            }
        """
        for room in rooms:
            if len(room) > self._room_max_size:
                pass
            else:
                pass


    def sit_down(self, user):
        """
        Example:
            self._node_hash_room
            {
                1: { 'room1': [u1,u2,u3,u4], 'room2':[...]},
                2: { 'room5': [u1,u2,u3,u4], 'room6':[...]},
                3: { 'room8': [u1,u2,u3,u4], 'room9':[...]}
            }
        """
        for node in self._node_hash_room:
            if node in self._machine_hash_connect:
                # node connect okay!
                rooms = self._node_hash_room[node]
                if len(rooms) > self._node_max_size:
                    # Current node fill out!
                    pass
                else:
                    self.in_node(rooms, user)
                    room = manager.check_in(user)
                    self._node_hash_room[node].add(room)    # a set !!
                    return #TODO ...
            else:
                # keep look next node
                pass

    
    def stand_up(self, user, room, node):
        _node = self._node_hash_room[node]
        room_name = manager.check_out(user)
        room = manager.game_rooms[room_name]
        if len(room) == 0:
            self._node_hash_room[node].remove(room)


if __name__ == '__main__':
    mmt = NodeManager()
    mmt.register('connect1', '127.0.0.1','9001')
    mmt.register('connect2', '127.0.0.1','9002')
    print mmt._machine_hash_connect 
    print mmt._node_hash_room 
    mmt.unregister('connect2')
    mmt.register('connect2a', '127.0.0.1','9002')
    print mmt._node_hash_room
    #print mmt.is_full()
    #mmt.build_room()
    #print mmt._node_room
