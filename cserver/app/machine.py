class MachineManager(object):
    """
    @property _node_id
    This property will important to keep our node server work fine!
    Assume we have some situation like below.
    1, room server die, we try to connect it. after we reconnect success
    we don't want it rearrange our node id! so you will try to send a argument
    with the connect of http/websocket. so we have the below url!
    `ws://127.0.0.1:8888/ws?ip=127.0.0.1&port=9001&mode=1`
    mode = 1 is a example, maybe another! but for the first time, we send a `-1`
    as the argument! and that url will direct to `register`, and generate a node id!
    2, we run before room-server, the reconnect has try many time, but the `mode=-1`
    send to the room-server. so the room-server will understand we has not register!
    3, if the room-server die, it's hope to recovery by our data! so that's why we has this!
    """
    _node_id = -1

    """
    To keep the _node_id, only be changed at the first time!
    """
    _set_node_flag = True
    _set_machine_flag = True

    _room_hash_uid_set = {}
    _uid_hash_room = {}
    _handler_hash_connect = {}
    _handler_hash_uid = {}
    _uid_hash_handler = {}
    _user_counter = 0
    _room_counter = 0
    _room_set = set()
    """
    @property _machine
    The machine id by host and port split by `-`
    it's should id by self also can from the room-server!
    """
    _machine = '127.0.0.1-0000'
    """
    @property _room_max_size
    The max size if the game room!
    This value should always be the same with `room-server`
    should when the connect has success! the room-server should
    let the local machine know that value!
    """
    _room_max_size = 8

    def set_node(self, node):
        """
        This is singleton pattern method! only first time has effective!
        so that can keep the node id work for all-life!
        Args:
            node:

        Returns:

        """
        if self._set_node_flag:
            self._node_id = node
            self._set_node_flag = False

    def set_machine(self, machine):
        if self._set_machine_flag:
            self._machine = machine
            self._set_machine_flag = False

    def check_in(self, connect, room, uid):
        self._handler_hash_connect[id(connect)] = connect
        self._uid_hash_handler[uid] = connect
        self._handler_hash_uid[id(connect)] = uid
        self._uid_hash_room[uid] = room
        if room in self._room_hash_uid_set:
            self._room_hash_uid_set[room].add(uid)
        else:
            self._room_counter += 1
            self._room_set.add(room)
            self._room_hash_uid_set[room] = set()
            self._room_hash_uid_set[room].add(uid)
        self._user_counter += 1
        response = {"command": "ack_check_in", "uid": uid}
        self.send(response)

    def check_out(self, connect):
        handler = id(connect)
        uid = self._handler_hash_uid[handler]
        room = self._uid_hash_room[uid]
        del self._uid_hash_room[uid]
        del self._uid_hash_handler[uid]
        del self._handler_hash_uid[handler]
        del self._handler_hash_connect[handler]
        self._room_hash_uid_set[room].remove(uid)
        response = {"command": "ack_check_out", "uid": uid}
        self._user_counter -= 1
        self.send(response)

    def help_recovery(self):
        """
        Send all local data to room server to recovery it!
        Returns:
            {
            "command": "ack_recovery",  # command
            "node": 2,  # Node id
            "user": 18,  # user number
            "rooms": ["r1", "r2", "r3"],  # room set
            "counter": 64,  # the total room in node
            "machine": "127.0.0.1-9001",  # machine id

            "room_hash_user_set" : {"room1": ["user1", "user2"],"room2":[...]},
             "user_hash_room" : {"user1": "room1", "user1":"room1", "user2":"room2},

             //"room_hash_lack_level":{"room1": 1,"room2":2}
             //self._room_counter = 4
             //self._user_counter = 8
             @1 you can't according the total of each node roo_counter to get that value
             because, that result maybe less than the actually value!
             @2 you can't according the currently max-room-id to get the that value too.
             cause ,we no sure every-node restart success ~~when the room-server die~
             maybe die too~~
             """
        return {
            "command": "ack_recovery",  # command
            "node": self._node_id,  # Node id
            "user": self._user_counter,  # user number
            "rooms": self._room_set,  # room set
            "counter": self._room_counter,  # the total room in node
            "machine": self._machine,  # machine id
            "room_hash_uid_set": self._room_hash_uid_set,
            "uid_hash_room": self._uid_hash_room,
        }
