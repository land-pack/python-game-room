
class RoomManager(object):
    """
    Each run has 6 key
    """
    #keys_set = []
    
    fragmentary_room = {}
    check_table = {}
    game_rooms = {}
    index = 0
    current_counter = 0
    
    def __init__(self, size=4, num=100):
        """
        @param size: The size of each room
        @param num: The number of room
        """
        self.size = size
        self.hang_keys()


    def hang_keys(self):
        """
        {   
            1: ['room1', 'room5'],
            2: ['room2', 'room3'],
            3: ['room4', 'room6', 'room7'],
            4: ['room8'],
            5: [],
        }
        """
        self.fragmentary_room = { i:[]  for i in range(self.size) }
   
    
    def has_fragmentary(self):
        """
        Available keys
        """
        key_levels = [i for i in xrange(self.size)]
        for key_level in key_levels:
            room_names = self.fragmentary_room.get(key_level)
            if room_names:
                room_name = room_names.pop()
                if key_level > 1:
                    self.fragmentary_room(key - 1).push(room_name)
                return room_name
        return None

    
    def new_room_name(self, prefix='room', subfix=''):
        index = RoomManager.index
        return '%s%s%s' % ( prefix, index, subfix)

    
    def new_room(self, room_name, uid):
        if RoomManager.current_counter == 0:
            room_name = self.new_room_name()
            self.game_rooms[room_name] = [uid, ]
            RoomManager.current_counter = RoomManager.current_counter + 1
        elif RoomManager.current_counter <= self.size:
            room_name = self.new_room_name()
            self.game_rooms[room_name].append(uid)
            RoomManager.current_counter = RoomManager.current_counter + 1
        else:
            RoomManager.current_counter = 0
            RoomManager.index = RoomManager.index + 1
            room_name = self.new_room_name()
            self.game_rooms[room_name] = [uid, ]

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
            self.new_room(room_name, uid)


    def check_out(self, uid):
        room_name = self.check_table[uid]
        self.game_rooms[room_name].remove(uid)
        residue = self.game_rooms[room_name]
        if residue == 0:
            #drop the room
            pass
        else:
            room_level = self.size - len(residue)
            self.fragmentary_room[room_level].append(room_name)
        del self.check_table[uid]



if __name__ == '__main__':
    manager = RoomManager()
    manager.check_in(12344)
    manager.check_in(12355)
    manager.check_in(12366)
    manager.check_in(12388)
    manager.check_in(12399)
    manager.check_in(12300)
    print manager.game_rooms
    manager.check_out(12388)
    print manager.game_rooms
    manager.check_in(12888)
    print manager.game_rooms
    manager.check_in(22299)
    print manager.game_rooms
    manager.check_in(88800)
    print manager.game_rooms
