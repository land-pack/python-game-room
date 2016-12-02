from node import NodeManager
from room import RoomManager
from core import DispatchCommand


class RoomServer(RoomManager, NodeManager, DispatchCommand):
    """
    RoomServer
    As name implicate, it's responsible dispatch room! and the player
    can check-in/check-out! the system can kick some one! and also
    responsible release source!
    @Begin
        rs = RoomServer()
        rs.register()
        rs.check_in()
        rs.check_out()
        rs.unregister()
        rs.kick_off()
        rs.recovery_node()
        rs._recovery_room()
    """

    def __init__(self, node_max_room=32, node_max_user=320, room_size=10):
        self._node_max_size = node_max_room
        self._node_max_user_number = node_max_user
        self._room_max_size = room_size
        self.config_room(size=room_size)


if __name__ == '__main__':
    print "manager = RoomServer(size=3, prefix='room_')"
    manager = RoomServer()
    print "manager.check_in(12)"
    manager.check_in(12)
    manager.room_status()
    print '=' * 50
    print ''
    print "manager.check_out(12)"
    manager.check_out(12)
    manager.room_status()
    print '=' * 50
    print ''
    print "manager.check_in(12)"
    manager.check_in(12)
    print "manager.check_in(13)"
    manager.check_in(13)
    manager.room_status()
    print '=' * 50
    print ''
    print "manager.check_out(12)"
    manager.check_out(12)
    print "manager.check_out(13)"
    manager.check_out(13)
    manager.room_status()

    print '=' * 50
    print ''
    print "check_in(0 ~ 9)"
    for i in range(10):
        manager.check_in(i)
        manager.room_status()
    manager.room_status()

    print '=' * 50
    print ''
    print "check_out(0 ~ 9)"
    for i in range(10):
        manager.check_out(i)
        manager.room_status()
    manager.room_status()

    print '=' * 50
    print ''
    print "check_in(0 ~ 9)"
    for i in range(10):
        manager.check_in(i)
        manager.room_status()
    manager.room_status()

    print '=' * 50
    print ''
    print "check_in(100 ~ 110)"
    for i in range(100, 110):
        manager.check_in(i)
        manager.room_status()
    manager.room_status()
