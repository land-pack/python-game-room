class LocalManager(object):
    
    """
    @property _room_hash_user
    Example:
        {
            r1 : [u1, u2, u3 ],
            r2 : [u4, u5, u6 ],
            r3 : [u7, u8, u9 ],
        }
    """
    _room_hash_user = {}
    """
    @property _user_hash_room
    Example:
        {
            u1: r1,
            u2: r1,
            u3: r2,
            u4: r2,
        }
    """
    _user_hash_room = {}
    """
    @property _connect_hash_uid
    Example:
        {
            connect1: u1,
            connect2: u2,
            connect3: u3,
        }
    """
    _connect_hash_uid = {}
    """
    @property _websocket_handler_hash_uid
    Example:
        {
            connect1: u1,
            connect2: u2,
            connect3: u3,
        }
    """
    _uid_hash_websocket_handler = {}
    


    def __init__(self, node_id=None):
        self.node_id = node_id


    def check_in(self, connect, room, uid):
        if room in self._room_hash_user:
            self._room_hash_user[room].add(uid)
        else:
            self._room_hash_user[room] = set()
            self._room_hash_user[room].add(uid)
        
        self._connect_hash_uid[id(connect)] = uid
        self._uid_hash_websocket_handler[uid] = connect 
        self._user_hash_room[uid] = room            
        return {"command": "check_in", "uid": uid}


    def check_out(self, connect):
        """
        if the connect hash cut off, then check_out this user!
        """
        uid = self._connect_hash_uid[id(connect)]
        room = self._user_hash_room[uid]
        self._room_hash_user[room].remove(uid)
        del self._user_hash_room[uid]
        del self._uid_hash_websocket_handler[uid]
        #TODO sync remove to data server
        return {"command": "check_out", "uid": uid}
    
    
    def candidate(self):
        pass


    def sync_from_data_server(self):
        pass


    def sync_to_data_server(self):
        data = {"_user_hash_room": self._user_hash_room,
                "_room_hash_room": self._room_hash_room}
        return data


    def kid_off(self, uid):
        pass


    def chat_with(self, from_uid, to_uid, message):
        if to_uid in self._uid_hash_websocket_handler:
            to_handler = self._uid_hash_websocket_handler[to_uid]
            to_handler.write_message(message)
        else:
            return None


if __name__ == '__main__':
    node_id = 1
    lm = LocalManager(node_id)
    lm.check_in('r1', 'u1')
    lm.check_in('r1', 'u2')
    lm.check_in('r1', 'u3')
    lm.check_in('r1', 'u4')
    print lm._user_hash_room
    print lm._room_hash_user
