class RoomManager(object):
    """
    Each run has 6 key
    """
    
    check_table = {}
    game_rooms = {}
    room_level = {}
    index = 0
    current_counter = 0
    
    def __init__(self, size=5, num=100, prefix=''):
        """
        @param size: The size of each room, 
        @param num: The number of room
        """
        #: Because python index start with `0` so 
        #: self.size = size -1
        self.size = size - 1
        self.room_size = self.size + 1
        self.fragmentary_room = { i:[]  for i in range(1, self.size + 1) }
        self.available_level = xrange(self.size)
        self.prefix = prefix


    def has_fragmentary(self):
        """
        Fragmentary keys, Check if available!
        You should check fragmentary_room before use new room!
        """
        for key_level in self.available_level:
            room_names = self.fragmentary_room.get(key_level)
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
            we should delete this member from self.fragmentary_room 
            """
            room_name = self.fragmentary_room.get(key_level).pop()
        
        
        elif key_level > 1 and key_level <= self.room_size:
            """
            """
            room_name = self.fragmentary_room.get(key_level).pop()
            self.fragmentary_room[key_level - 1].append(room_name)
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
        index = self.index
        return '%s%s%s' % ( prefix, index, subfix)

    
    def new_room(self, uid):
        """
        @param room_name: a string type, 
        Example:    'room1'
        @param uid: a string or a number set!
        Example: 12345
        return : None
        """
        if self.game_rooms == {}:
            self.index = 0
            self.current_counter = 0

        if self.current_counter == 0:
            room_name = self.new_room_name()
            self.game_rooms[room_name] = [uid, ]
            self.current_counter = self.current_counter + 1

        elif self.current_counter <= self.size:
            room_name = self.new_room_name()
            self.game_rooms[room_name].append(uid)
            self.current_counter = self.current_counter + 1
        else:
            self.current_counter = 0
            self.index = self.index + 1
            room_name = self.new_room_name()
            self.game_rooms[room_name] = [uid, ]
            self.current_counter = self.current_counter + 1

        self.check_table[uid] = room_name

    def check_in(self, uid):
        """
        @param uid: user id
        """
        room_name = self.has_fragmentary()
        if room_name:
            # fill out fragmentary room!
            self.game_rooms[room_name].append(uid)
            self.check_table[uid] = room_name
        else:
            # get new room
            self.new_room(uid)

        return self.check_table[uid]

    
    def rotation(self, room_name, key_level):
        level = self.room_level.get(room_name, '')
        if level:
            self.fragmentary_room[level].remove(room_name)
        self.fragmentary_room[key_level].append(room_name)
        self.room_level[room_name] = key_level 

    
    def clean(self, room_name):
        length = len(self.game_rooms[room_name])
        if length == 0:
            del self.game_rooms[room_name]
            level = self.room_level.get(room_name, '')
            if level:
                self.fragmentary_room[level].remove(room_name)
                del self.room_level[room_name]
        elif length == 5:
            pass
        else:
            key_level = self.room_size - length
            self.rotation(room_name, key_level)

    
    def check_out(self, uid):
        try:
            room_name = self.check_table[uid]
        except Exception as ex:
            raise KeyError('check_table has no such key [%s]' % uid)
        try:
            self.game_rooms[room_name].remove(uid)
        except Exception as ex:
            raise KeyError('room [%s] have no found any memeber name as [%s]' % (room_name, uid))
        self.clean(room_name)
        del self.check_table[uid]
        return room_name


    def status(self):
        print '-' * 80
        print 'game_rooms:',    self.game_rooms
        print 'fragmentary:',   self.fragmentary_room
        print 'check_table',    self.check_table
        print 'room_level',     self.room_level
        print '-' * 80

if __name__ == '__main__':
    manager = RoomManager(size=3, prefix='room_')
    manager.check_in(12)
    manager.check_in(13)
    manager.check_in(14)
    print manager.check_in(15)
    print manager.check_in(16)
    manager.status()
    manager.check_out(16)
    manager.status()
    print manager.check_out(15)
    manager.status()
