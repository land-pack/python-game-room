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
    
    def __init__(self, size=3, rooms=3, prefix=''):
        """
        @param size: The size of each room, 
        @param num: The number of room
        """
        #: Because python _room_counter start with `0` so 
        #: self.size = size -1
        self.size = size - 1
        self.room_size = self.size + 1
        self._lack_level_hash_room_set = { i:[]  for i in range(1, self.size + 2) }
        self._lack_level_set = xrange(size + 1)
        self._max_lack_level = size
        self.prefix = prefix
        self.rooms = rooms


    def get_fragmentary(self):
        """
        Fragmentary keys, Check if available!
        You should check _lack_level_hash_room_set before use new room!
        """
        for _lack_level in self._lack_level_set:
            _room_set = self._lack_level_hash_room_set.get(_lack_level)
            if _room_set:
                print 'see me ...'
                room_name = self.select_room_name(_lack_level)
                return room_name
        return None


    def select_room_name(self, _lack_level):
        """
        Rotation the key_level
        Example:
           origin    ->> {1:['r1', 'r2', 'r3'], 2:['r4', 'r5'] ... }
           rotation: ->> {1:['r1', 'r2', 'r3', 'r4'], 2:['r5'] ... }

        """

        if _lack_level == 1:
            """
            If the `_lack_level` is equal to `1`, and then after pop out
            it's should be use for some one! so we can use `pop` to return it
            & delete it from self._lack_level_hash_room_set 
            """
            room_name = self._lack_level_hash_room_set.get(_lack_level).pop()
            del self._room_hash_lack_level[room_name]
            return room_name
        
        
        elif _lack_level > 1 and _lack_level <= self._max_lack_level:
            """
            if this `_lack_level` range between 1 to self._max_lack_level
            we can do some rotation, after return it!
            """
            room_name = self._lack_level_hash_room_set.get(_lack_level).pop()
            new_lack = _lack_level - 1
            self._lack_level_hash_room_set[new_lack].append(room_name)
            self._room_hash_lack_level[room_name]=new_lack
            return room_name
        else:
            return None
        

    def generate_room_name(self, subfix=''):
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

        if self._room_hash_user_set == {}:

            self._room_counter = 0
            self._user_counter = 0

        if self._user_counter == 0:
            room_name = self.generate_room_name()
            self._room_hash_user_set[room_name] = [uid, ]
            self._user_counter = self._user_counter + 1

        elif self._user_counter <= self.size:
            room_name = self.generate_room_name()
            self._room_hash_user_set[room_name].append(uid)
            self._user_counter = self._user_counter + 1
        else:

            self._user_counter = 0
            self._room_counter = self._room_counter + 1
            room_name = self.generate_room_name()
            self._room_hash_user_set[room_name] = [uid, ]
            self._user_counter = self._user_counter + 1
        self._user_hash_room[uid] = room_name
    

    def clean(self, room_name):
        """
        @param room_name: room id
        @return : None
        After a user out, the system will clean some trash of the user!
        """
        if room_name in self._room_hash_lack_level:
            old_level = self._room_hash_lack_level[room_name]
            self._lack_level_hash_room_set[old_level].remove(room_name)
            new_level = old_level + 1
            self._lack_level_hash_room_set[new_level].append(room_name)
            self._room_hash_lack_level[room_name]=new_level
        else:
            length = len(self._room_hash_user_set[room_name])
            lack_level = self.room_size - length
            self._lack_level_hash_room_set[lack_level].append(room_name)
            self._room_hash_lack_level[room_name]=lack_level


    
    def check_in(self, uid):
        """
        @param uid: user id
        @return : room id 
        """
        room_name = self.get_fragmentary()
        if room_name:
            # fill out fragmentary room!
            print 'room_name', room_name 
            self._room_hash_user_set[room_name].append(uid)
            self._user_hash_room[uid] = room_name
            self._user_counter = self._user_counter + 1
        else:
            # get new room
            self.new_room(uid)
        return self._user_hash_room[uid]
    
    

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


class RoomManager(_BaseRoomManager):

    def status(self):
        print '+' * 50
        print '_room_hash_user_set:',    self._room_hash_user_set
        print '_user_hash_room',    self._user_hash_room
        print '_room_hash_lack_level',     self._room_hash_lack_level
        print '_lack_level_hash_room_set', self._lack_level_hash_room_set
        print '+' * 50 



if __name__ == '__main__':
    print "manager = RoomManager(size=3, prefix='room_')"
    manager = RoomManager(size=3, rooms=3, prefix='room_')
    print "manager.check_in(12)"
    manager.check_in(12)
    manager.status()
    print '='*50
    print ''
    print "manager.check_out(12)"
    manager.check_out(12)
    manager.status()
    print '='*50
    print ''
    print "manager.check_in(12)"
    manager.check_in(12)
    print "manager.check_in(13)"
    manager.check_in(13)
    manager.status()
    print '='*50
    print ''
    print "manager.check_out(12)"
    manager.check_out(12)
    print "manager.check_out(13)"
    manager.check_out(13)
    manager.status()

    print '='*50
    print ''
    print "check_in(0 ~ 9)"
    for i in range(10):
        manager.check_in(i)
        manager.status()
    manager.status()
    
    print '='*50
    print ''
    print "check_out(0 ~ 9)"
    for i in range(10):
        manager.check_out(i)
        manager.status()
    manager.status()
    
    print '='*50
    print ''
    print "check_in(0 ~ 9)"
    for i in range(10):
        manager.check_in(i)
        manager.status()
    manager.status()
    
    print '='*50
    print ''
    print "check_in(100 ~ 110)"
    for i in range(100,110):
        manager.check_in(i)
        manager.status()
    manager.status()
