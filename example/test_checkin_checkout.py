from room_demo import RoomManager


manager = RoomManager()

for i in xrange(10):
    manager.check_in(i)

manager.status()

manager.check_out(1)
manager.status()

manager.check_out(2)
manager.status()

manager.check_out(0)
manager.status()

manager.check_out(3)
manager.status()

manager.check_out(4)
manager.status()

for i in xrange(10):
    manager.check_in(i)
manager.status()
