class _BaseRoomManager(object):
    """
    @property _user_hash_room
    Usage:
    Example:
            {
                "u1": "r1",
                "u2": "r2",
                "u3": "r3",
            }
    """
    _user_hash_room = {}
    """
    @property _room_hash_user_set
    Usage:
    Example:
            {
                "r1": [u1, u2],
                "r2": [u3, u4],
                "r3": [u5,],
            }
    """
    _room_hash_user_set = {}
    """
    @property _room_hash_lack_level
    Usage:
    Example:
            {
                "r1": 0,
                "r2": 2,
                "r3": 1,
            }
    """
    _room_hash_lack_level = {}
    """
    @property _lack_level_hash_room_set 
    Usage:
    Example:
            {
                1: [r1, r4],
                2: [r2, r3],
                3: [r5, r6],
            }
    """
    _lack_level_hash_room_set = {}
    """
    @property _room_counter
    Usage:  
    Example:    2
    """
    _room_counter = 0
    """
    @property _room_counter
    Usage:  
    Example:    2
    """
    _user_counter = 0
    
    def __init__(self, size=5, num=100, prefix=''):
        """
        @param size: The size of each room, 
        @param num: The number of room
        """
        #: Because python _room_counter start with `0` so 
        #: self.size = size -1
        self.size = size - 1
        self.room_size = self.size + 1
        self._lack_level_hash_room_set = { i:[]  for i in range(1, self.size + 2) }
        self.available_level = xrange(self.size + 2)
        self.prefix = prefix


    def has_fragmentary(self):
        """
        Fragmentary keys, Check if available!
        You should check _lack_level_hash_room_set before use new room!
        """
        for key_level in self.available_level:
            room_names = self._lack_level_hash_room_set.get(key_level)
            if room_names:
                room_name = self.do_it(key_level)
                return room_name
        return None

    def do_it(self, key_level):
        """
        Rotation the key_level
        Example:
           origin    ->> {1:['r1', 'r2', 'r3'], 2:['r4', 'r5'] ... }
           rotation: ->> {1:['r1', 'r2', 'r3', 'r4'], 2:['r5'] ... }

        """

        if key_level == 1:
            """
            If the `key_level` is equal to `1`, that's mean
            we should delete this member from self._lack_level_hash_room_set 
            """
            room_name = self._lack_level_hash_room_set.get(key_level).pop()
        
        
        elif key_level > 1 and key_level <= self.room_size:
            """
            """
            room_name = self._lack_level_hash_room_set.get(key_level).pop()
            self._lack_level_hash_room_set[key_level - 1].append(room_name)
        else:
            raise KeyError("key level out of range")
        
        return room_name
        
    def new_room_name(self, subfix=''):
        """
        @param prefix: default `room`, you can define it if you want!
        @param subfix: default ``, a empty string!
        @return : a string with a number which increment auto!
        """
        prefix = self.prefix
        _room_counter = self._room_counter
        return '%s%s%s' % ( prefix, _room_counter, subfix)

    
    def new_room(self, uid):
        """
        @param room_name: a string type, 
        Example:    'room1'
        @param uid: a string or a number set!
        Example: 12345
        return : None
        """
        print '_user_counter', self._user_counter
        if self._room_hash_user_set == {}:
            self._room_counter = 0
            self._user_counter = 0

        if self._user_counter == 0:
            room_name = self.new_room_name()
            self._room_hash_user_set[room_name] = [uid, ]
            self._user_counter = self._user_counter + 1

        elif self._user_counter <= self.size:
            room_name = self.new_room_name()
            self._room_hash_user_set[room_name].append(uid)
            self._user_counter = self._user_counter + 1
        else:
            self._user_counter = 0
            self._room_counter = self._room_counter + 1
            room_name = self.new_room_name()
            self._room_hash_user_set[room_name] = [uid, ]
            self._user_counter = self._user_counter + 1

        self._user_hash_room[uid] = room_name

    def check_in(self, uid):
        """
        @param uid: user id
        """
        room_name = self.has_fragmentary()
        if room_name:
            # fill out fragmentary room!
            self._room_hash_user_set[room_name].append(uid)
            self._user_hash_room[uid] = room_name
        else:
            # get new room
            self.new_room(uid)

        return self._user_hash_room[uid]

    
    def rotation(self, room_name, key_level):
        level = self._room_hash_lack_level.get(room_name, '')
        if level:
            self._lack_level_hash_room_set[level].remove(room_name)
        self._lack_level_hash_room_set[key_level].append(room_name)
        self._room_hash_lack_level[room_name] = key_level 

    
    def clean(self, room_name):
        length = len(self._room_hash_user_set[room_name])
        if length == 0:
            del self._room_hash_user_set[room_name]
            level = self._room_hash_lack_level.get(room_name, '')
           # if level:
           #     self._lack_level_hash_room_set[level].remove(room_name)
           #     del self._room_hash_lack_level[room_name]
        elif length == self.room_size:
            pass
        else:
            print 'length ...', length
            key_level = self.room_size - length
            self.rotation(room_name, key_level)

    
    def check_out(self, uid):
        try:
            room_name = self._user_hash_room[uid]
        except Exception as ex:
            raise KeyError('_user_hash_room has no such key [%s]' % uid)
        try:
            self._room_hash_user_set[room_name].remove(uid)
        except Exception as ex:
            raise KeyError('room [%s] have no found any memeber name as [%s]' % (room_name, uid))
        self.clean(room_name)
        del self._user_hash_room[uid]
        return room_name


    def status(self):
        print '-' * 80
        print '_room_hash_user_set:',    self._room_hash_user_set
        print 'fragmentary:',   self._lack_level_hash_room_set
        print '_user_hash_room',    self._user_hash_room
        print '_room_hash_lack_level',     self._room_hash_lack_level
        print '-' * 80

if __name__ == '__main__':
    manager = RoomManager(size=3, prefix='room_')
    manager.check_in(12)
    manager.check_in(13)
    manager.check_in(14)
    manager.check_in(15)
    manager.check_in(16)
    manager.status()
    manager.check_out(16)
    manager.status()
    manager.check_out(15)
    manager.status()
    manager.check_in(161)
    manager.check_in(162)
    manager.check_in(163)
    manager.status()
