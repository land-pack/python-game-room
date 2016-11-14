import sys
sys.path.append("..")
import unittest
from lib.node import NodeManager
from lib.room import RoomManager

class WebSocketHandler(object):
    pass

class Test_NodeManager(unittest.TestCase):
    def setUp(self):
        pass


    def test_register(self):
        mmt = NodeManager()
        handler = WebSocketHandler()
        mmt.register(handler, "127.0.0.1", 9001)
        #self.assertEqual(mmt._machine_hash_connect, {'127.0.0.1-9001': 140073898507168, '127.0.0.1-9002': 140073898507312})
	#self.assertEqual(mmt._connect_hash_machine, {140073898507168: '127.0.0.1-9001', 140073898507312: '127.0.0.1-9002'})
	self.assertEqual(mmt._machine_hash_node, {'127.0.0.1-9001': 0})
        mmt.register(handler, "127.0.0.1", 9002)
	self.assertEqual(mmt._machine_hash_node, {'127.0.0.1-9001': 0, '127.0.0.1-9002': 1})
	self.assertEqual(mmt._node_hash_room, {0: [], 1: []})

 
class Test_NodeManager_RoomManager(unittest.TestCase):
    def test_install_room(self):
        mmt2 = NodeManager()
        manager = RoomManager()
        mmt2.register("connect1", "127.0.0.1", 9001)
        room = manager.check_in("u1")
        response = mmt2.install_room(room, "u1")
        self.assertEqual(response, {'node': 0, 'ip': '127.0.0.1', 'port': '9001', 'room': '0'})
        



if __name__ == '__main__':
    unittest.main()
