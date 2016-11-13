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
    @property _node_hash_counter
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
    The max number can live on one node!
    """
    _node_max_size = 2


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
            node_id = self._machine_hash_node[key]
            return node_id

        else:
            """
            This node is first time come to the server
            so register as new one!
            """
            node_id = self._node_index
            self._machine_hash_node[key] = self._node_index
            self._node_hash_room[self._node_index] = []
            self._connect_hash_machine[id(connect)] = key
            self._machine_hash_connect[key] = id(connect)
            self._node_hash_machine[self._node_index]=key
            self._node_hash_counter[self._node_index]= 0
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


    def add_user(self, user):
        """
        @param user: user id
        @return:
            0+ : node id
            -1 : no node for use!
        """
        if user in self._user_hash_node:
            return self._user_hash_node[user]
        for node in self._node_hash_counter:
            if self._node_hash_counter[node] < self._node_max_size:
                ip, port = self._node_hash_machine[node].split("-")
                return {"node":node, "ip":ip, "port": port}
            else:
                # keep looking next node
                pass
        return -1


    def del_user(self, user):
        del self._user_hash_node[user]

    
    def node_room_counter(self, node, room_counter):
        """
        @param node: node id
        @param room_counter: current node room total numbers!
        return: 0
        """
        try:
            self._node_hash_counter[node] = room_counter
            return 0
        except Exception as ex:
            return -1


if __name__ == '__main__':
    mmt = NodeManager()
    mmt.register('connect1', '127.0.0.1','9001')
    mmt.register('connect2', '127.0.0.1','9002')
    print mmt._machine_hash_connect 
    print mmt._node_hash_room 
    mmt.unregister('connect2')
    mmt.register('connect2a', '127.0.0.1','9002')
    print mmt._node_hash_room
    # --------------------
    print '-'*50
    print mmt._node_hash_counter
    mmt.add_user('user1')
    print mmt._node_hash_counter
    print 'update room counter '
    mmt.node_room_counter(0,2)
    print mmt._node_hash_counter
    mmt.node_room_counter(0,5)
    print mmt._node_hash_counter
    
    
    
