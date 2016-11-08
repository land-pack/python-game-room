from room_demo import RoomManager


manager = RoomManager()

manager.check_in(123)
manager.status()
manager.check_out(123)
manager.status()
for i in xrange(10):
    manager.check_in(i)

#manager.check_in(123)
manager.status()
for i in xrange(4):
    manager.check_out(i)
manager.status()

"""
Sample Output:
game_rooms: {'room0': [4], 'room1': [5, 6, 7, 8, 9]}
fragmentary: {1: [], 2: [], 3: [], 4: ['room0']}
check_table {4: 'room0', 5: 'room1', 6: 'room1', 7: 'room1', 8: 'room1', 9: 'room1'}
room_level {'room0': 4}

Describe:
You can see we have only one member into the 'room0', see `fragmentary` field
we have a special Dicts-Type. 4: ['room0'] mean we have 4 seats available!
and the next test code, will achieve the follow target:
@1, if all member get out from some room, whether we can clean that room!
@2, if all member get out from some room, whether we can reset fragmentary flag!
@3, if all ... whether we can reset room_level
"""
manager.check_out(4)
manager.status()
"""
Sample Output:
game_rooms: {'room1': [5, 6, 7, 8, 9]}
fragmentary: {1: [], 2: [], 3: [], 4: ['room0']}
check_table {5: 'room1', 6: 'room1', 7: 'room1', 8: 'room1', 9: 'room1'}
room_level {}
Describe:
For now, we have achieve some part of above target!

"""
