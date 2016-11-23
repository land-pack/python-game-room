python-game-room/client/                                                                            000755  000765  000024  00000000000 13015015762 016456  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/client/client_side/                                                                000755  000765  000024  00000000000 13015015762 020740  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/client/only_request_room.py                                                        000755  000765  000024  00000000661 13015015762 022623  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import requests 
import ujson
import threading
import time
from forgery_py import name as fgname


def join_request():
    uid = fgname.full_name()
    response = requests.get('http://127.0.0.1:8888/api/join?uid=%s' % uid)
    print '*'*100
    print response.content


if __name__ == '__main__':

    for i in xrange(20):
        threading.Thread(target=join_request, args=(), name='thread-' + str(i)).start()
        time.sleep(1)
                                                                               python-game-room/client/single-user.py                                                              000755  000765  000024  00000002127 13015015762 021272  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import requests 
import ujson
from client_side.websocket import RTCWebSocketClient
from tornado import ioloop


def dispatch(*args):
    print args



def main():
    uid = raw_input("Please input your uid:")
    response = requests.get('http://127.0.0.1:8888/api/join?uid=%s' % uid)
    """
    {
        "ip":"127.0.0.1",
        "port":9001,
        "node":1,
        "room":3
    }
    """
    data = response.content
    print 'data', data
    data = ujson.loads(data)
    if data == -1:
        print 'Currently no more node for use'
    else:
        ip = data['ip']
        port = data['port']
        node = data['node']
        room = data['room']
        print 'node[%s]---room[%s]' % (node, room) 
    
    io_loop = ioloop.IOLoop.instance()
    client = RTCWebSocketClient(io_loop)
    ws_url = "ws://127.0.0.1:9000/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip,port,node,room,uid)
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10, dispatch=dispatch)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
                                                                                                                                                                                                                                                                                                                                                                                                                                         python-game-room/client/client_side/__init__.py                                                     000644  000765  000024  00000000000 13015015762 023037  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/client/client_side/websocket.py                                                    000644  000765  000024  00000014010 13015015762 023274  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import time
import functools
import json
import ujson
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket

APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self._ws_connection = None
        self._connect_status = self.DISCONNECTED
        self.dispatch = dispatch


    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        self._connect_status = self.CONNECTING
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(self._io_loop, request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)

    def send(self, data):
        """Send message to the server
        :param str data: message.
        """

        if self._ws_connection:
            self._ws_connection.write_message(json.dumps(data))

    def close(self, reason=''):
        """Close connection.
        """

        if self._connect_status != self.DISCONNECTED:
            self._connect_status = self.DISCONNECTED
            self._ws_connection and self._ws_connection.close()
            self._ws_connection = None
            self.on_connection_close(reason)

    def _connect_callback(self, future):
        if future.exception() is None:
            self._connect_status = self.CONNECTED
            self._ws_connection = future.result()
            self.on_connection_success()
            self._read_messages()
        else:
            self.close(future.exception())

    def is_connected(self):
        return self._ws_connection is not None

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self.close()
                break

            self.on_message(msg)

    def on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """

        pass

    def on_connection_success(self):
        """This is called on successful connection ot the server.
        """

        pass

    def on_connection_close(self, reason):
        """This is called when server closed the connection.
        """
        pass


class RTCWebSocketClient(WebSocketClient):
    msg = {'command': 'msg', 'from': 'Frank ak',
           'to': 'Peter', 'body': 'Hello, Peter'}
    hb_msg = {'command': 'ping'}  # hearbeat

    message = ''

    heartbeat_interval = 3
    
    node_id = 0

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self.ws_url = None
        self.auto_reconnet = False
        self.last_active_time = 0
        self.pending_hb = None

        super(RTCWebSocketClient, self).__init__(self._io_loop,
                                                 self.connect_timeout,
                                                 self.request_timeout)

    def connect(self, url, dispatch, auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        self.dispatch = dispatch

        super(RTCWebSocketClient, self).connect(self.ws_url)

    def send(self, msg):
        super(RTCWebSocketClient, self).send(msg)
        self.last_active_time = time.time()

    def on_message(self, msg):
        self.last_active_time = time.time()
       # data = ujson.loads(msg)
       # if 'node_id' in data:
       #     self.node_id= data.get("node_id")
       # else:
       #     print 'From Center>>>', msg
        self.dispatch(self, msg)

    def on_connection_success(self):
        print('Connected!')
        #self.send(self.msg)
        self.last_active_time = time.time()
        self.send_heartbeat()

    def on_connection_close(self, reason):
        print('Connection closed reason=%s' % (reason,))
        self.pending_hb and self._io_loop.remove_timeout(self.pending_hb)
        self.reconnect()

    def reconnect(self):
        print 'reconnect'
        if not self.is_connected() and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval,
                                     super(RTCWebSocketClient, self).connect, self.ws_url)

    def send_heartbeat(self):
        if self.is_connected():
            now = time.time()
            if (now > self.last_active_time + self.heartbeat_interval):
                self.last_active_time = now
                self.send(self.hb_msg)

            self.pending_hb = self._io_loop.call_later(self.heartbeat_interval, self.send_heartbeat)



def dispatch(websocket_handler, message):
    print '>>>>I am dispatch', message

def main():
    io_loop = ioloop.IOLoop.instance()

    client = RTCWebSocketClient(io_loop)
    #ws_url = 'ws://127.0.0.1:8090/ws'
    ws_url = 'ws://echo.websocket.org'
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10, dispatch=dispatch)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        python-game-room/cserver/                                                                           000755  000765  000024  00000000000 13015015762 016651  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/cserver/app/                                                                       000755  000765  000024  00000000000 13015015762 017431  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/cserver/lib/                                                                       000755  000765  000024  00000000000 13015015762 017417  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/cserver/log.conf                                                                   000644  000765  000024  00000001367 13015015762 020310  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         [loggers]
keys = root, cserver

#################################
[root]
[logger_root]
level=DEBUG
handlers = hand01, hand02


[logger_cserver]
handlers=hand01, hand02
qualname=cserver
propagate=0


#################################


[handlers]
keys = hand01, hand02

[handler_hand01]
class=StreamHandler
level=DEBUG
formatter=form01
args=(sys.stderr,)


[handler_hand02]
class=handlers.RotatingFileHandler
level=INFO
formatter=form01
args=('../log/cserver.log','a', 10*1024*1024, 5)

##################################

[formatters]
keys = form01, form02

[formatter_form01]
format=%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s
datefmt=%a, %d %b %Y %H:%M:%S

[formatter_form02]
format=%(name)-12s: %(levelname)-8s %(message)s
datefmt=
                                                                                                                                                                                                                                                                         python-game-room/cserver/manager.py                                                                 000755  000765  000024  00000006443 13015015762 020647  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import socket
import os
import ujson
import logging
import logging.config

from tornado import ioloop
from tornado import websocket
from tornado import web
from tornado.options import options, define
#from lib.views import dc # to trigger the DispatchCommand 
#from lib.views import lm as lsystem
#from lib.chat import tm
#from lib.chat import TalkManager
import lib.color
from app.system import LocalSystem

lsystem = LocalSystem()


logging.config.fileConfig("log.conf")
logger = logging.getLogger("cserver")

define(name="port", default=9001, help="default port", type=int)
define(name="cport", default=8888, help="default port", type=int)



g_client_connect = []
g_connect_hash_uid = {}



options.parse_command_line()






"""
    Delegate Server ----------WebSocket-------> Area Server
"""


class DelegateWebSocketHandler(websocket.WebSocketHandler):
    """
    This websocket server orient to client-side!
    client A --------------               ----- Delegate Server A
                           } nginx ---> {
    client B --------------               ----- Delegate Server B
    """

    _connect_hash_uid = {}


    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        Usage: The argument with url only for `nginx` identify it!
        Example:
            url="ws://127.0.0.1:8880/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip, port, node, room, uid)
            ws = websocket.WebSocketApp(url)
        """
        uid = self.get_argument("uid")
        room = self.get_argument("room")
        response = lm.check_in(self, room, uid)
        g_client_connect.append(self)
        g_connect_hash_uid[id(self)]=uid
        #self._node_id = websocket_client.node_id
        websocket_client.send(response)


    def on_close(self):
        """
        If someone leave out, will send heartbeat/ if time out after servaral try
        will notifiy the area-server! and if the area-server has acknowledge this operation
        and then this uid will remove from local processs memory!
        Example:
            if acknowledge == True:
                local_hash.remove(some_one)
            else:
                wait.. 
        """
       # response = lm.check_out(self)
        g_client_connect.remove(self)
        del g_connect_hash_uid[id(self)]
        #uid = clients[id(self)]
        #msg = {"command": "check_out", "uid": uid}
        #make_redirect(msg, token)
        # log.this uid, if timeout ,will notify boss server
        #req = {"command":"del_uid",
        #        #"node":self._node_id,
        #        "uid":g_connect_hash_uid[id(self)]
        #    }

        print ' send client close notify  to server'
        #websocket_client.send(response)



    def on_message(self, msg):
        #data = ujson.loads(msg)
        #uid= data.get("uid")
        #    websocket_client.send(req)
        #response = ujson.dumps({"command":"in"})
        #tm.render(msg)
        #self.write_message(response)
       # response = tm.render(msg, lm)
        if response:
            self.write_message(response)


def main():
    application = web.Application([
        (r'/ws', DelegateWebSocketHandler),
        ],
        debug=True)
    application.listen(options.port)

    io_loop = ioloop.IOLoop.current()
    lsystem.run()
    io_loop.start()

if __name__ == '__main__':
    main()
                                                                                                                                                                                                                             python-game-room/cserver/lib/__init__.py                                                            000644  000765  000024  00000000000 13015015762 021516  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/cserver/lib/chat.py                                                                000644  000765  000024  00000001401 13015015762 020704  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         from core import TalkManager

tm = TalkManager()



@tm.route("ping")
def ping(message, lm):
    return {"command": "pong"}


@tm.route("chat_with")
def chat_with(message, lm):
    """
    @param message: a dict-type
        {   
            "command": "chat_with",
            "content": "hello another guys",
            "to_uid": "xxxxx"
        }
    """
    print "recv a chat with command"
    to_uid = message.get("to_uid")
    from_uid = message.get("from_uid")
    message = "hello "
    response = lm.chat_with(from_uid, to_uid, message)
    if response:
        return {"command":"chat_with", "status":"ok"}
    else:
        return {"command": "chat_with", "status":"bad","info":"no such user"}

@tm.route("broadcast")
def broadcast(message, lm):
    pass

                                                                                                                                                                                                                                                               python-game-room/cserver/lib/color.py                                                               000644  000765  000024  00000007361 13015015762 021116  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python
# encoding: utf-8
import logging
# now we patch Python code to add color support to logging.StreamHandler
def add_coloring_to_emit_windows(fn):
        # add methods we need to the class
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE      = 0x0001 # text color contains blue.
        FOREGROUND_GREEN     = 0x0002 # text color contains green.
        FOREGROUND_RED       = 0x0004 # text color contains red.
        FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
        FOREGROUND_WHITE     = FOREGROUND_BLUE|FOREGROUND_GREEN |FOREGROUND_RED
       # winbase.h
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # wincon.h
        FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE      = 0x0001
        FOREGROUND_GREEN     = 0x0002
        FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED       = 0x0004
        FOREGROUND_MAGENTA   = 0x0005
        FOREGROUND_YELLOW    = 0x0006
        FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

        BACKGROUND_BLACK     = 0x0000
        BACKGROUND_BLUE      = 0x0010
        BACKGROUND_GREEN     = 0x0020
        BACKGROUND_CYAN      = 0x0030
        BACKGROUND_RED       = 0x0040
        BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW    = 0x0060
        BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080 # background color is intensified.     

        levelno = args[1].levelno
        if(levelno>=50):
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY 
        elif(levelno>=40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno>=30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno>=20):
            color = FOREGROUND_GREEN
        elif(levelno>=10):
            color = FOREGROUND_MAGENTA
        else:
            color =  FOREGROUND_WHITE
        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color( FOREGROUND_WHITE )
        #print "after"
        return ret
    return new

def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno>=50):
            color = '\x1b[31m' # red
        elif(levelno>=40):
            color = '\x1b[31m' # red
        elif(levelno>=30):
            color = '\x1b[33m' # yellow
        elif(levelno>=20):
            color = '\x1b[32m' # green 
        elif(levelno>=10):
            color = '\x1b[35m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].msg = color + args[1].msg +  '\x1b[0m'  # normal
        #print "after"
        return fn(*args)
    return new

import platform
if platform.system()=='Windows':
    # Windows does not support ANSI escapes and we are using API calls to set the console color
    logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
else:
    # all non-Windows platforms are supporting ANSI escapes so we use them
    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)
    #log = logging.getLogger()
    #log.addFilter(log_filter())
    #//hdlr = logging.StreamHandler()
    #//hdlr.setFormatter(formatter())
                                                                                                                                                                                                                                                                               python-game-room/cserver/lib/core.py                                                                000644  000765  000024  00000002717 13015015762 020730  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import ujson


class DispatchCommand(object):
    
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route

    
    def dispatch(self, handler, message, lm):
        data = ujson.loads(message)
        command = data.get("command")
        if command in self._command_hash_views:
            self._command_hash_views[command](handler, data, lm)
        else:
           #handler.send("404 Error")
            print "404--Can't parser command[%s]" % command
            print "data complete is [%s]" % data
   


class TalkManager(object):
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route
    
   
    def render(self, message, mmt):
        data = ujson.loads(message)
        print '>>>>>>>>>>>>', data
        command = data.get("command")
        if command in self._command_hash_views:
            data = self._command_hash_views[command](data, mmt)
        else:
            data = {"command":"nothing"}

        if data:
            response = ujson.dumps(data)
            return response
        else:
            return None
        
                                                 python-game-room/cserver/lib/local.py                                                               000644  000765  000024  00000005326 13015015762 021071  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         class LocalManager(object):
    
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
    """
    @property node_id
    When the register success! this value will set! do never change !
    Default is `-1`, when it register succes, should be large than `0`!
    """
    node_id = -1
    

    def __init__(self):
        pass


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
                                                                                                                                                                                                                                                                                                          python-game-room/cserver/lib/machine.py                                                             000644  000765  000024  00000000102 13015015762 021366  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         class MachineManager(object):
    """
    """
    _node_id = None
                                                                                                                                                                                                                                                                                                                                                                                                                                                              python-game-room/cserver/lib/main.py                                                                000644  000765  000024  00000001216 13015015762 020715  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import socket
import time
from tornado import ioloop
from websocket import RTCWebSocketClient



def run(cport=8888, port=9001, dc=None):
    host=socket.gethostname()
    ip=socket.gethostbyname(host)
    ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s&mode=%s' % (cport, ip, port, -1)
    ws_recovery_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s&mode=' % (cport, ip, port)
    
    websocket_client = RTCWebSocketClient()
    websocket_client.connect(ws_url, ws_recovery_url, dispatch=dc.dispatch, auto_reconnet=True, reconnet_interval=10)
    io_loop = ioloop.IOLoop.instance()
    token = RTCWebSocketClient(io_loop)
    return io_loop, websocket_client 

                                                                                                                                                                                                                                                                                                                                                                                  python-game-room/cserver/lib/system.py                                                              000755  000765  000024  00000002733 13015015762 021325  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import socket
import ujson
from tornado import ioloop
from websocket import RTCWebSocketClient
from machine import MachineManager


class LocalSystem(RTCWebSocketClient, MachineManager):
    """
    """
    _command_hash_views = {}
    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route


    def dispatch(self, message):
        data = ujson.loads(message)
        command = data.get("command","something")
        if command in self._command_hash_views:
            self._command_hash_views[command](handler, data)
        else:
            #handler.send("404 Error")
            print "404--Can't parser command[%s]" % command

   
    def run(self, rsp=8888, port=9001, dc=None):
        """
        @param rsp: room server port
        @param port: current server listen port
        @return None
        """
        #io_loop = ioloop.IOLoop.current().instance()
        host=socket.gethostname()
        ip=socket.gethostbyname(host)
        ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s&mode=%s' % (cport, ip, port, -1)
        self.connect(ws_url, auto_reconnet=True, reconnet_interval=10)


if __name__ == '__main__':

    lsystem = LocalSystem()
    lsystem.run()
    io_loop = ioloop.IOLoop.current().instance()
    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


                                     python-game-room/cserver/lib/views.py                                                               000644  000765  000024  00000004035 13015015762 021130  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import logging
from core import DispatchCommand
from websocket import lm


dc = DispatchCommand()
logger = logging.getLogger("cserver")
global __connect_mode 



@dc.route("pong")
def pong(handler, request, lm):
    data = {"command": "ping"}
    #handler.send(data)


@dc.route("connect")
def connect(handler, request, lm):
    status = request.get("status")
    if status == 'ok':
        __connect_mode = request.get("mode")
        print '__connect_mode', __connect_mode 
        if __connect_mode == 'recovery':
            logger.info('Reconnect successfully')
            logger.debug(">>>>%s" % node_id)
            #TODO sync local data to remote server
        else:
            logger.info('Connect successfully')
            node_id = request.get("node")

            lm.node_id = node_id
            #TODO register basic information which given 
            # from the remote server!
    else:
        pass


@dc.route("sync_all")
def sync_all(handler, request, lm):
    data = {"command": "ack_sync"}
    handler.send(data)

@dc.route("close")
def close(handler, request):
    pass

@dc.route("ack_check_in")
def ack_check_in(handler, request, lm):
    status = request.get("status")
    if status == "ok":
        # check in user local
        pass
    else:
        #TODO let the client know ~~~
        pass

@dc.route("ack_check_out")
def ack_check_out(handler, request, lm):
    status = request.get("status")
    if status == "ok":
        #TODO do some clean job on local
        pass
    else:
        #TODO Don't need to let the client know ~~~
        pass

@dc.route("recovery")
def recovery(handler, request, lm):
    print 'reconnect success'
    print 'try recovery data ...'
    data = {
                "command": "ack_recovery",
                "node": "2",
                "user": 18,
                "rooms": ["r1", "r2", "r3"],
                "counter": 2,
                "machine": "127.0.0.1-9002"


            }
    handler.send(data)


@dc.route("ack_recovery")
def ack_recovery(handler, request, lm):
    print 'recovery success ..!'

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   python-game-room/cserver/lib/websocket.py                                                           000644  000765  000024  00000013611 13015015762 021761  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import time
import logging
import functools
import json
import ujson
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket


logger = logging.getLogger("cserver")


APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self._ws_connection = None
        self._connect_status = self.DISCONNECTED


    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        self._connect_status = self.CONNECTING
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(self._io_loop, request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)


    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if self._ws_connection:
            self._ws_connection.write_message(ujson.dumps(data))

    
    def close(self, reason=''):
        """Close connection.
        """

        if self._connect_status != self.DISCONNECTED:
            self._connect_status = self.DISCONNECTED
            self._ws_connection and self._ws_connection.close()
            self._ws_connection = None
            self.on_connection_close(reason)


    def _connect_callback(self, future):
        if future.exception() is None:
            self._connect_status = self.CONNECTED
            self._ws_connection = future.result()
            self.on_connection_success()
            self._read_messages()
        else:
            self.close(future.exception())

    
    def is_connected(self):
        return self._ws_connection is not None


    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self.close()
                break
            self.on_message(msg)


    def on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        pass


    def on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass


    def on_connection_close(self, reason):
        """This is called when server closed the connection.
        """
        pass


class RTCWebSocketClient(WebSocketClient):
    hb_msg = {'command': 'ping'}  # hearbeat
    message = ''
    heartbeat_interval = 3
    

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self.ws_url = None
        self.auto_reconnet = False
        self.last_active_time = 0
        self.pending_hb = None

        super(RTCWebSocketClient, self).__init__(self._io_loop,
                                                 self.connect_timeout,
                                                 self.request_timeout)

    def connect(self, url, auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        super(RTCWebSocketClient, self).connect(self.ws_url)


    def send(self, msg):
        super(RTCWebSocketClient, self).send(msg)
        self.last_active_time = time.time()


    def on_message(self, msg):
        self.last_active_time = time.time()
        self.dispatch(msg)


    def on_connection_success(self):
        logger.info('Connect ...')
        self.last_active_time = time.time()
        self.send_heartbeat()

    
    def on_connection_close(self, reason):
        logger.warning('Connection closed reason=%s' % (reason,))
        self.pending_hb and self._io_loop.remove_timeout(self.pending_hb)
        self.reconnect()

    def reconnect(self):
        logger.info('Reconnect')
        #self.ws_url = self.ws_recovery_url + lm.node_id
        #logger.info("Send node id [%s] to remote server" % lm.node_id)
        if not self.is_connected() and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval,
                                     super(RTCWebSocketClient, self).connect, self.ws_url)

    def send_heartbeat(self):
        if self.is_connected():
            now = time.time()
            if (now > self.last_active_time + self.heartbeat_interval):
                self.last_active_time = now
                self.send(self.hb_msg)

            self.pending_hb = self._io_loop.call_later(self.heartbeat_interval, self.send_heartbeat)



    def dispatch(self,  message):
        """
        You must  override this method!
        """
        pass


def main():
    io_loop = ioloop.IOLoop.instance()
    client = RTCWebSocketClient(io_loop)
    ws_url = 'ws://127.0.0.1:8888/ws?ip=127.0.0.1&port=9001&mode=1'
    #ws_url = 'ws://echo.websocket.org'
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
                                                                                                                       python-game-room/cserver/lib/websocket_bk.py                                                        000644  000765  000024  00000014544 13015015762 022443  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import time
import logging
import functools
import json
import ujson
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket
from local import LocalManager

lm = LocalManager()

logger = logging.getLogger("cserver")


APPLICATION_JSON = 'application/json'

DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self._ws_connection = None
        self._connect_status = self.DISCONNECTED
        self.dispatch = dispatch


    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        self._connect_status = self.CONNECTING
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(self._io_loop, request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)


    def send(self, data):
        """Send message to the server
        :param str data: message.
        """

        if self._ws_connection:
            self._ws_connection.write_message(json.dumps(data))

    
    def close(self, reason=''):
        """Close connection.
        """

        if self._connect_status != self.DISCONNECTED:
            self._connect_status = self.DISCONNECTED
            self._ws_connection and self._ws_connection.close()
            self._ws_connection = None
            self.on_connection_close(reason)

    def _connect_callback(self, future):
        if future.exception() is None:
            self._connect_status = self.CONNECTED
            self._ws_connection = future.result()
            self.on_connection_success()
            self._read_messages()
        else:
            self.close(future.exception())

    
    def is_connected(self):
        return self._ws_connection is not None

    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self.close()
                break

            self.on_message(msg)

    def on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """

        pass

    def on_connection_success(self):
        """This is called on successful connection ot the server.
        """

        pass

    def on_connection_close(self, reason):
        """This is called when server closed the connection.
        """
        pass


class RTCWebSocketClient(WebSocketClient):
    msg = {'command': 'msg', 'from': 'Frank ak',
           'to': 'Peter', 'body': 'Hello, Peter'}
    hb_msg = {'command': 'ping'}  # hearbeat

    message = ''

    heartbeat_interval = 3
    

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self.ws_url = None
        self.auto_reconnet = False
        self.last_active_time = 0
        self.pending_hb = None

        super(RTCWebSocketClient, self).__init__(self._io_loop,
                                                 self.connect_timeout,
                                                 self.request_timeout)

    def connect(self, url, recovery_url, dispatch,  auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.ws_recovery_url = recovery_url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        self.dispatch = dispatch

        super(RTCWebSocketClient, self).connect(self.ws_url)

    def send(self, msg):
        super(RTCWebSocketClient, self).send(msg)
        self.last_active_time = time.time()

    def on_message(self, msg):
        self.last_active_time = time.time()
       # data = ujson.loads(msg)
       # if 'node_id' in data:
       #     self.node_id= data.get("node_id")
       # else:
       #     print 'From Center>>>', msg
        self.dispatch(self, msg, self.lm)

    def on_connection_success(self):
        logger.info('Connect ...')
        #print 'connect ..'
        #self.send(self.msg)
        self.last_active_time = time.time()
        self.send_heartbeat()

    def on_connection_close(self, reason):
        logger.warning('Connection closed reason=%s' % (reason,))
        self.pending_hb and self._io_loop.remove_timeout(self.pending_hb)
        self.reconnect()

    def reconnect(self):
        logger.info('Reconnect')
        self.ws_url = self.ws_recovery_url + lm.node_id
        logger.info("Send node id [%s] to remote server" % lm.node_id)
        if not self.is_connected() and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval,
                                     super(RTCWebSocketClient, self).connect, self.ws_url)

    def send_heartbeat(self):
        if self.is_connected():
            now = time.time()
            if (now > self.last_active_time + self.heartbeat_interval):
                self.last_active_time = now
                self.send(self.hb_msg)

            self.pending_hb = self._io_loop.call_later(self.heartbeat_interval, self.send_heartbeat)



def dispatch(websocket_handler, message):
    logger.debug('Recv: %s' % message)


def main():
    io_loop = ioloop.IOLoop.instance()
    client = RTCWebSocketClient(io_loop)
    #ws_url = 'ws://127.0.0.1:8090/ws'
    ws_url = 'ws://echo.websocket.org'
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10, dispatch=dispatch)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
                                                                                                                                                            python-game-room/cserver/app/__init__.py                                                            000644  000765  000024  00000000000 13015015762 021530  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/cserver/app/machine.py                                                             000644  000765  000024  00000000102 13015015762 021400  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         class MachineManager(object):
    """
    """
    _node_id = None
                                                                                                                                                                                                                                                                                                                                                                                                                                                              python-game-room/cserver/app/system.py                                                              000755  000765  000024  00000002731 13015015762 021335  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import socket
import ujson
from tornado import ioloop
from websocket import RTCWebSocketClient
from machine import MachineManager


class LocalSystem(RTCWebSocketClient, MachineManager):
    """
    """
    _command_hash_views = {}
    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route


    def dispatch(self, message):
        data = ujson.loads(message)
        command = data.get("command","something")
        if command in self._command_hash_views:
            self._command_hash_views[command](handler, data)
        else:
            #handler.send("404 Error")
            print "404--Can't parser command[%s]" % command

   
    def run(self, rsp=8888, port=9001, dc=None):
        """
        @param rsp: room server port
        @param port: current server listen port
        @return None
        """
        #io_loop = ioloop.IOLoop.current().instance()
        host=socket.gethostname()
        ip=socket.gethostbyname(host)
        ws_url = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s&mode=%s' % (rsp, ip, port, -1)
        self.connect(ws_url, auto_reconnet=True, reconnet_interval=10)


if __name__ == '__main__':

    lsystem = LocalSystem()
    lsystem.run()
    io_loop = ioloop.IOLoop.current().instance()
    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


                                       python-game-room/cserver/app/views.py                                                               000644  000765  000024  00000000001 13015015762 021127  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               python-game-room/cserver/app/websocket.py                                                           000644  000765  000024  00000013611 13015015762 021773  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import time
import logging
import functools
import json
import ujson
from tornado import gen
from tornado import httpclient
from tornado import httputil
from tornado import ioloop
from tornado import websocket


logger = logging.getLogger("cserver")


APPLICATION_JSON = 'application/json'
DEFAULT_CONNECT_TIMEOUT = 30
DEFAULT_REQUEST_TIMEOUT = 30


class WebSocketClient(object):
    """Base for web socket clients.
    """

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self._ws_connection = None
        self._connect_status = self.DISCONNECTED


    def connect(self, url):
        """Connect to the server.
        :param str url: server URL.
        """
        self._connect_status = self.CONNECTING
        headers = httputil.HTTPHeaders({'Content-Type': APPLICATION_JSON})
        request = httpclient.HTTPRequest(url=url,
                                         connect_timeout=self.connect_timeout,
                                         request_timeout=self.request_timeout,
                                         headers=headers)
        ws_conn = websocket.WebSocketClientConnection(self._io_loop, request)
        ws_conn.connect_future.add_done_callback(self._connect_callback)


    def send(self, data):
        """Send message to the server
        :param str data: message.
        """
        if self._ws_connection:
            self._ws_connection.write_message(ujson.dumps(data))

    
    def close(self, reason=''):
        """Close connection.
        """

        if self._connect_status != self.DISCONNECTED:
            self._connect_status = self.DISCONNECTED
            self._ws_connection and self._ws_connection.close()
            self._ws_connection = None
            self.on_connection_close(reason)


    def _connect_callback(self, future):
        if future.exception() is None:
            self._connect_status = self.CONNECTED
            self._ws_connection = future.result()
            self.on_connection_success()
            self._read_messages()
        else:
            self.close(future.exception())

    
    def is_connected(self):
        return self._ws_connection is not None


    @gen.coroutine
    def _read_messages(self):
        while True:
            msg = yield self._ws_connection.read_message()
            if msg is None:
                self.close()
                break
            self.on_message(msg)


    def on_message(self, msg):
        """This is called when new message is available from the server.
        :param str msg: server message.
        """
        pass


    def on_connection_success(self):
        """This is called on successful connection ot the server.
        """
        pass


    def on_connection_close(self, reason):
        """This is called when server closed the connection.
        """
        pass


class RTCWebSocketClient(WebSocketClient):
    hb_msg = {'command': 'ping'}  # hearbeat
    message = ''
    heartbeat_interval = 3
    

    def __init__(self, io_loop=None,
                 connect_timeout=DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=DEFAULT_REQUEST_TIMEOUT):

        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._io_loop = io_loop or ioloop.IOLoop.current()
        self.ws_url = None
        self.auto_reconnet = False
        self.last_active_time = 0
        self.pending_hb = None

        super(RTCWebSocketClient, self).__init__(self._io_loop,
                                                 self.connect_timeout,
                                                 self.request_timeout)

    def connect(self, url, auto_reconnet=True, reconnet_interval=10):
        self.ws_url = url
        self.auto_reconnet = auto_reconnet
        self.reconnect_interval = reconnet_interval
        super(RTCWebSocketClient, self).connect(self.ws_url)


    def send(self, msg):
        super(RTCWebSocketClient, self).send(msg)
        self.last_active_time = time.time()


    def on_message(self, msg):
        self.last_active_time = time.time()
        self.dispatch(msg)


    def on_connection_success(self):
        logger.info('Connect ...')
        self.last_active_time = time.time()
        self.send_heartbeat()

    
    def on_connection_close(self, reason):
        logger.warning('Connection closed reason=%s' % (reason,))
        self.pending_hb and self._io_loop.remove_timeout(self.pending_hb)
        self.reconnect()

    def reconnect(self):
        logger.info('Reconnect')
        #self.ws_url = self.ws_recovery_url + lm.node_id
        #logger.info("Send node id [%s] to remote server" % lm.node_id)
        if not self.is_connected() and self.auto_reconnet:
            self._io_loop.call_later(self.reconnect_interval,
                                     super(RTCWebSocketClient, self).connect, self.ws_url)

    def send_heartbeat(self):
        if self.is_connected():
            now = time.time()
            if (now > self.last_active_time + self.heartbeat_interval):
                self.last_active_time = now
                self.send(self.hb_msg)

            self.pending_hb = self._io_loop.call_later(self.heartbeat_interval, self.send_heartbeat)



    def dispatch(self,  message):
        """
        You must  override this method!
        """
        pass


def main():
    io_loop = ioloop.IOLoop.instance()
    client = RTCWebSocketClient(io_loop)
    ws_url = 'ws://127.0.0.1:8888/ws?ip=127.0.0.1&port=9001&mode=1'
    #ws_url = 'ws://echo.websocket.org'
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
                                                                                                                       python-game-room/example/                                                                           000755  000765  000024  00000000000 13015015762 016633  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/example/room_demo.py                                                               000644  000765  000024  00000011706 13015015762 021172  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         class RoomManager(object):
    """
    Each run has 6 key
    """
    
    check_table = {}
    game_rooms = {}
    room_level = {}
    index = 0
    current_counter = 0
    
    def __init__(self, size=5, num=100):
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
        
    def new_room_name(self, prefix='room', subfix=''):
        """
        @param prefix: default `room`, you can define it if you want!
        @param subfix: default ``, a empty string!
        @return : a string with a number which increment auto!
        """
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


    def status(self):
        print '-' * 80
        print 'game_rooms:',    self.game_rooms
        print 'fragmentary:',   self.fragmentary_room
        print 'check_table',    self.check_table
        print 'room_level',     self.room_level
        print '-' * 80
                                                          python-game-room/example/simple_test.py                                                             000644  000765  000024  00000002566 13015015762 021546  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         from room_demo import RoomManager


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
manager.check_in(4)
manager.status()

manager.check_out(5)
manager.status()

manager.check_in(88)
manager.status()

manager.check_in(99)
manager.status()
                                                                                                                                          python-game-room/example/test_checkin_checkout.py                                                   000644  000765  000024  00000000576 13015015762 023545  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         from room_demo import RoomManager


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
                                                                                                                                  python-game-room/requirements.txt                                                                   000644  000765  000024  00000000346 13015015762 020467  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         backports-abc==0.4
backports.ssl-match-hostname==3.5.0.1
certifi==2015.11.20.1
ForgeryPy==0.1
grasshopper==1.0.0
redis==2.10.5
requests==2.11.1
singledispatch==3.4.0.3
six==1.10.0
tornado==4.3
ujson==1.35
websocket-client==0.37.0
                                                                                                                                                                                                                                                                                          python-game-room/rserver/                                                                           000755  000765  000024  00000000000 13015015762 016670  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/rserver/app/                                                                       000755  000765  000024  00000000000 13015015762 017450  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/rserver/log.conf                                                                   000644  000765  000024  00000001367 13015015762 020327  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         [loggers]
keys = root, rserver

#################################
[root]
[logger_root]
level=DEBUG
handlers = hand01, hand02


[logger_rserver]
handlers=hand01, hand02
qualname=rserver
propagate=0


#################################


[handlers]
keys = hand01, hand02

[handler_hand01]
class=StreamHandler
level=DEBUG
formatter=form01
args=(sys.stderr,)


[handler_hand02]
class=handlers.RotatingFileHandler
level=INFO
formatter=form01
args=('../log/rserver.log','a', 10*1024*1024, 5)

##################################

[formatters]
keys = form01, form02

[formatter_form01]
format=%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s
datefmt=%a, %d %b %Y %H:%M:%S

[formatter_form02]
format=%(name)-12s: %(levelname)-8s %(message)s
datefmt=
                                                                                                                                                                                                                                                                         python-game-room/rserver/manager.py                                                                 000755  000765  000024  00000001506 13015015762 020661  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import os
import logging
import logging.config
from tornado.options import options, define
from tornado import web
from tornado import ioloop
from app.url import urls
from app.lib import color
from app.lib.utils import check_expire 
from app.views import manager 


logging.config.fileConfig("log.conf")
logger = logging.getLogger("rserver")
define(name="port", default=8888, help="default port", type=int)


if __name__ == '__main__':
    options.parse_command_line()
    application = web.Application(
                urls,
                debug=True,
                template_path=os.path.join(os.path.dirname(__name__),'app/templates'))

    logger.info('Listen on %s' %  options.port)
    application.listen(options.port)
    ioloop.PeriodicCallback(lambda :check_expire(manager) , 1000).start()
    ioloop.IOLoop.instance().start()
                                                                                                                                                                                          python-game-room/rserver/README.md                                                                  000644  000765  000024  00000000215 13015015762 020145  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         # Python Game Room Server

You can simple run it ~~

###How to use it?

*1, Run manager game room server

```
python manager.py --port=8888

                                                                                                                                                                                                                                                                                                                                                                                   python-game-room/rserver/app/__init__.py                                                            000644  000765  000024  00000000000 13015015762 021547  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/rserver/app/lib/                                                                   000755  000765  000024  00000000000 13015015762 020216  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/rserver/app/templates/                                                             000755  000765  000024  00000000000 13015015762 021446  5                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/rserver/app/url.py                                                                 000644  000765  000024  00000000513 13015015762 020623  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         from views import WebSocketHandler
from views import JoinHandler
from views import MonitorHandler
from views import DashHandler
from views import CSVHandler


urls = [
    (r'/ws', WebSocketHandler),
    (r'/api/join', JoinHandler),
    (r'/monitor', MonitorHandler),
    (r'/dash', DashHandler),
    (r'/data.csv', CSVHandler),
]
                                                                                                                                                                                     python-game-room/rserver/app/views.py                                                               000755  000765  000024  00000011564 13015015762 021171  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import os
import json
import datetime
import logging
import logging.config
import ujson
from tornado import web
from tornado import ioloop
from tornado import websocket

from lib.room import RoomManager
from lib.node import NodeManager
from lib.utils import set_expire, is_expire
from lib.views import dc
from lib.utils import check_expire



logger = logging.getLogger("rserver")



mmt = NodeManager()
manager = RoomManager(prefix='')
clients = []
client_handler_hash_connect = {}


class JoinHandler(web.RequestHandler):
    def get(self):
        """
        Usage:
            http://127.0.0.1:8880/api/join?uid=frank
        Desc:
            system will check MachineManagerTable to
            get the currently node for response the client!
            [User] ---http-----------> [Area] --------------
                                       {... }             ]
            token  <-----http------- MachineManagerTable ---

            [User] ---websocket ------>[Node] --------->[Area]

        Example:
        response={
                "ip": "127.0.0.1",
                "port": "9001",
                "node": "2",
                "room": "1",
            }
        """
        
        uid = self.get_argument("uid")
        room = manager.check_in(uid)
        response = mmt.landing(room, uid)
        print 'landing response', response
        if response == -1:
            # rollback ...
            manager.check_out(uid)
        #TODO let the delegate server know
        # try ..except should be here ...
        ip = response.get("ip")
        port = response.get("port")
        node = response.get("node")
        machine = "%s-%s" % (ip, port)
        client_handler = mmt._machine_hash_connect[machine]
        connect = client_handler_hash_connect[client_handler]
        connect.write_message(ujson.dumps({"uid":uid, "room":room, "node":node}))
        set_expire(uid)
        self.write(ujson.dumps(response))


class DashHandler(web.RequestHandler):
    def get(self):
        """
        manager.node.room.user,
        """
        output = ''
        lines = []
        tag = "id,value"
        lines.append(tag)
        root = "Manager"
        lines.append(root)
        for node in mmt._node_hash_room:
            rooms = mmt._node_hash_room[node]
            root2 = 'Manager.node_%s' % node
            lines.append(root2)
            for room in rooms:
                root3 = 'Manager.node_%s.room_%s' % (node, room)
                lines.append(root3)
                uids = manager._room_hash_user_set[room]
                for uid in uids:
                    output='Manager.node_%s.room_%s.uid_%s' % (node, room, uid)
                    lines.append(output)
        with open("./app/templates/data.csv", "w+") as fd:
            for line in lines:
                fd.write(line)
                fd.write("\n")
        self.render("dash.html")


class CSVHandler(web.RequestHandler):
    def get(self):
        self.render("data.csv")


class MonitorHandler(web.RequestHandler):
    def get(self):
        mmt.status()
        manager.status()
        self.write("ok")


class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    
    def open(self):
        """
        @param ip: node server ip
        @param port: node server port
        @param mode: the server connect mode
        'normally' will given if the machine is first time connect!
        'recovery' will given if the machine try to reconnect room server!
        to help room-server remeber something which its missing during some
        die~~
        
        Usage:
            ws = websocket.WebSocketApp("ws://127.0.0.1:8888/ws?ip=%s&port=%s&mode=%s" % (ip, port, mode)
        Desc:
            [Node] ----------------> [Area] --------
                                                    ]
            [Node] <--------------------------------
        """
        mode = self.get_argument('mode')
        logger.warning('current mode [%s]' %  mode)
        ip = self.get_argument('ip')
        port = self.get_argument("port")
        clients.append(self)
        client_handler_hash_connect[id(self)] = self
        if int(mode) == -1:
        # Normally mode
            node_id = mmt.register(self, ip, port, mode=mode)
            response = {"command":"connect", "status":"ok", "mode":"normally","node":node_id}
            self.write_message(ujson.dumps(response))
        else:
            node_id = mmt.register(self, ip, port, mode=mode)
            response = {"command":"connect", "status":"ok", "mode":"recovery"}
            self.write_message(ujson.dumps(response))



    def on_close(self):
        mmt.unregister(self)
        clients.remove(self)
        del client_handler_hash_connect[id(self)]


    def on_message(self, msg):
        print ' can i see this is', msg
        response = dc.render(msg, mmt, manager=manager)
        if response:
            self.write_message(response)
                                                                                                                                            python-game-room/rserver/app/templates/dash.html                                                    000644  000765  000024  00000003662 13015015762 023262  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         <!DOCTYPE html>
<meta charset="utf-8">
<style>

.node circle {
  fill: #999;
}

.node text {
  font: 10px sans-serif;
}

.node--internal circle {
  fill: #555;
}

.node--internal text {
  text-shadow: 0 1px 0 #fff, 0 -1px 0 #fff, 1px 0 0 #fff, -1px 0 0 #fff;
}

.link {
  fill: none;
  stroke: #555;
  stroke-opacity: 0.4;
  stroke-width: 1.5px;
}

</style>
<svg width="960" height="2000"></svg>
<script src="//d3js.org/d3.v4.min.js"></script>
<script>

var svg = d3.select("svg"),
    width = +svg.attr("width"),
    height = +svg.attr("height"),
    g = svg.append("g").attr("transform", "translate(40,0)");

var tree = d3.cluster()
    .size([height, width - 160]);

var stratify = d3.stratify()
    .parentId(function(d) { return d.id.substring(0, d.id.lastIndexOf(".")); });

d3.csv("data.csv", function(error, data) {
  if (error) throw error;

  var root = stratify(data)
      .sort(function(a, b) { return (a.height - b.height) || a.id.localeCompare(b.id); });

  tree(root);

  var link = g.selectAll(".link")
      .data(root.descendants().slice(1))
    .enter().append("path")
      .attr("class", "link")
      .attr("d", function(d) {
        return "M" + d.y + "," + d.x
            + "C" + (d.parent.y + 100) + "," + d.x
            + " " + (d.parent.y + 100) + "," + d.parent.x
            + " " + d.parent.y + "," + d.parent.x;
      });

  var node = g.selectAll(".node")
      .data(root.descendants())
    .enter().append("g")
      .attr("class", function(d) { return "node" + (d.children ? " node--internal" : " node--leaf"); })
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })

  node.append("circle")
      .attr("r", 2.5);

  node.append("text")
      .attr("dy", 3)
      .attr("x", function(d) { return d.children ? -8 : 8; })
      .style("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d) { return d.id.substring(d.id.lastIndexOf(".") + 1); });
});

</script>
                                                                              python-game-room/rserver/app/templates/data.csv                                                     000644  000765  000024  00000001751 13015015762 023100  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         id,value
Manager
Manager.node_0
Manager.node_0.room_0
Manager.node_0.room_0.uid_Rebecca Medina
Manager.node_0.room_0.uid_Carolyn Wood
Manager.node_0.room_0.uid_Deborah Wagner
Manager.node_0.room_1
Manager.node_0.room_1.uid_Virginia Sanchez
Manager.node_0.room_1.uid_Stephanie Howell
Manager.node_0.room_1.uid_Ruby Perkins
Manager.node_0.room_2
Manager.node_0.room_2.uid_Carolyn King
Manager.node_0.room_2.uid_Kenneth Hanson
Manager.node_0.room_2.uid_Melissa Spencer
Manager.node_0.room_3
Manager.node_0.room_3.uid_Jacqueline Martin
Manager.node_0.room_3.uid_Michelle Kelley
Manager.node_0.room_3.uid_Ryan Ruiz
Manager.node_0.room_4
Manager.node_0.room_4.uid_Christina Morrison
Manager.node_0.room_4.uid_Sarah Murphy
Manager.node_0.room_4.uid_Deborah Garcia
Manager.node_0.room_5
Manager.node_0.room_5.uid_Diana Ross
Manager.node_0.room_5.uid_Denise Schmidt
Manager.node_0.room_5.uid_Janice Stevens
Manager.node_0.room_6
Manager.node_0.room_6.uid_Diana Watson
Manager.node_0.room_6.uid_Donna Carpenter
                       python-game-room/rserver/app/lib/__init__.py                                                        000644  000765  000024  00000000000 13015015762 022315  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         python-game-room/rserver/app/lib/color.py                                                           000644  000765  000024  00000007361 13015015762 021715  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         #!/usr/bin/env python
# encoding: utf-8
import logging
# now we patch Python code to add color support to logging.StreamHandler
def add_coloring_to_emit_windows(fn):
        # add methods we need to the class
    def _out_handle(self):
        import ctypes
        return ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
    out_handle = property(_out_handle)

    def _set_color(self, code):
        import ctypes
        # Constants from the Windows API
        self.STD_OUTPUT_HANDLE = -11
        hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

    setattr(logging.StreamHandler, '_set_color', _set_color)

    def new(*args):
        FOREGROUND_BLUE      = 0x0001 # text color contains blue.
        FOREGROUND_GREEN     = 0x0002 # text color contains green.
        FOREGROUND_RED       = 0x0004 # text color contains red.
        FOREGROUND_INTENSITY = 0x0008 # text color is intensified.
        FOREGROUND_WHITE     = FOREGROUND_BLUE|FOREGROUND_GREEN |FOREGROUND_RED
       # winbase.h
        STD_INPUT_HANDLE = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE = -12

        # wincon.h
        FOREGROUND_BLACK     = 0x0000
        FOREGROUND_BLUE      = 0x0001
        FOREGROUND_GREEN     = 0x0002
        FOREGROUND_CYAN      = 0x0003
        FOREGROUND_RED       = 0x0004
        FOREGROUND_MAGENTA   = 0x0005
        FOREGROUND_YELLOW    = 0x0006
        FOREGROUND_GREY      = 0x0007
        FOREGROUND_INTENSITY = 0x0008 # foreground color is intensified.

        BACKGROUND_BLACK     = 0x0000
        BACKGROUND_BLUE      = 0x0010
        BACKGROUND_GREEN     = 0x0020
        BACKGROUND_CYAN      = 0x0030
        BACKGROUND_RED       = 0x0040
        BACKGROUND_MAGENTA   = 0x0050
        BACKGROUND_YELLOW    = 0x0060
        BACKGROUND_GREY      = 0x0070
        BACKGROUND_INTENSITY = 0x0080 # background color is intensified.     

        levelno = args[1].levelno
        if(levelno>=50):
            color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY 
        elif(levelno>=40):
            color = FOREGROUND_RED | FOREGROUND_INTENSITY
        elif(levelno>=30):
            color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
        elif(levelno>=20):
            color = FOREGROUND_GREEN
        elif(levelno>=10):
            color = FOREGROUND_MAGENTA
        else:
            color =  FOREGROUND_WHITE
        args[0]._set_color(color)

        ret = fn(*args)
        args[0]._set_color( FOREGROUND_WHITE )
        #print "after"
        return ret
    return new

def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if(levelno>=50):
            color = '\x1b[31m' # red
        elif(levelno>=40):
            color = '\x1b[31m' # red
        elif(levelno>=30):
            color = '\x1b[33m' # yellow
        elif(levelno>=20):
            color = '\x1b[32m' # green 
        elif(levelno>=10):
            color = '\x1b[35m' # pink
        else:
            color = '\x1b[0m' # normal
        args[1].msg = color + args[1].msg +  '\x1b[0m'  # normal
        #print "after"
        return fn(*args)
    return new

import platform
if platform.system()=='Windows':
    # Windows does not support ANSI escapes and we are using API calls to set the console color
    logging.StreamHandler.emit = add_coloring_to_emit_windows(logging.StreamHandler.emit)
else:
    # all non-Windows platforms are supporting ANSI escapes so we use them
    logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)
    #log = logging.getLogger()
    #log.addFilter(log_filter())
    #//hdlr = logging.StreamHandler()
    #//hdlr.setFormatter(formatter())
                                                                                                                                                                                                                                                                               python-game-room/rserver/app/lib/core.py                                                            000644  000765  000024  00000002025 13015015762 021517  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import ujson


class DispatchCommand(object):
    
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route
    
   
    def render(self, message, mmt, manager=None):
        data = ujson.loads(message)
        command = data.get("command")
        if command in self._command_hash_views:
            data = self._command_hash_views[command](data, mmt, manager)
        else:
            data = {"command":"nothing"}
        if data:
            response = ujson.dumps(data)
            return response
        

if __name__ == '__main__':
    dc = DispatchCommand()
    @dc.route("add")
    def add(handler, data):
        print 'i am add',data
    
    @dc.route("sub")
    def add(handler, data):
        print 'i am sub', data


    message = ujson.dumps({"command":"xxsub","someting":"aaa"})
    dc.dispatch(None, message)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           python-game-room/rserver/app/lib/node.py                                                            000644  000765  000024  00000022134 13015015762 021517  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         class BaseMachineHashNodeManager(object):
    """
    @property _machine_hash_node
    Example:
            {
                '127.0.0.1-9001':0,
                '127.0.0.1-9002':1,
                '127.0.0.1-9003':2,
            }
    """
    _machine_hash_node = {}
    """
    @property _node_hash_machine
    Example:
            {
                0: '127.0.0.1-9001'
                1: '127.0.0.1-9002'
                2: '127.0.0.1-9003'
            }
    """
    _node_hash_machine = {}

    """
    @property _node_hash_room
    Examle:
            {
                0: ['room1', 'room2', ...],
                1: ['room11', 'room12', ...],
                2: ['room21', 'room22', ...],
            }
    """
    _node_hash_room = {}
    """
    @property _connect_hash_machine
    Example:
            {
                4388089088:'127.0.0.1-9001',
                4388089089:'127.0.0.1-9002',
                4388089090:'127.0.0.1-9003',
            }
    """
    _connect_hash_machine = {}
    """
    @property _machine_hash_connect
    Example:
            {
               '127.0.0.1-9001': 4388089088,
               '127.0.0.1-9001': 4388089089,
               '127.0.0.1-9001': 4388089090,
            }
    """
    _machine_hash_connect = {}
    """
    @property _node_hash_counter
    The counter of room in the node!
    After a new room append to this node
    this property will auto increment!
    Example:
            { 0 : 64 }
            { 1 : 64 }
            { 2 : 32 }
            { 3 : 0  }
            { 4 : 0  }
    """
    _node_hash_counter = {}

    """
    @property _node_index:
    Auto increment
    """
    _node_index = 0


    def __init__(self, rooms=2, users=32):
        self._node_max_size = rooms
        self._node_max_user_number = users


    def register(self, connect, ip, port, mode=-1):
        """
        @param ip: proxy server ip
        @param port: proxy server port
        @param mode: -1 --> normaly, 0+ --> recovery
        @return: None
        """
        if mode == -1:
            node_id = self._node_index
        else:
            node_id = mode
        key = "%s-%s" % (ip, port)
        if key in self._machine_hash_connect:
            """
            This node has already register to the server
            so ignore this register instead mark it as alive!
            """
            self._connect_hash_machine[id(connect)] = key   # recreate ...
            self._machine_hash_connect[key] = id(connect)   # update ...
            node_id = self._machine_hash_node[key]
            return node_id

        else:
            """
            This node is first time come to the server
            so register as new one!
            """
            self._machine_hash_node[key] = node_id
            self._node_hash_room[node_id] = []
            self._connect_hash_machine[id(connect)] = key
            self._machine_hash_connect[key] = id(connect)
            self._node_hash_machine[node_id]=key
            self._node_hash_counter[node_id]= 0    # 0 room number!
            self._node_hash_user[node_id]= 0    # 0 user number!
            if mode == -1:
                self._node_index = self._node_index + 1
            return node_id
    
    
    def unregister(self, connect):
        """
        @param connect: websocket connect
        if websocket disconnect, we will remove this item
        from self._machine_hash_connect & self._connect_hash_machine!
        after do this, we actully mark it as un-live! but it's
        still store on the memory so, next time it come back
        still got the same node name!
        Example:
            [Node123] -----> [127.0.0.1:90001]
                ....disconnect....
                ....reconnect..... 
            [Node123] -----> [127.0.0.1:90001]
        """
        del self._connect_hash_machine[id(connect)]


class NodeManager(BaseMachineHashNodeManager):

    """
    @property _user_hash_node
    Example:
            { u1 : 0,
              u2 : 0,
              u3 : 1 
            }
    """
    _user_hash_node = {}
    """
    @property _room_hash_node
    Example:
            { 0 : 0,
              1 : 0,
              2 : 1 
            }
    """
    _room_hash_node = {}
    """
    @property _node_hash_user
    Example:
            { 0 : 32 }
            { 1 : 9  }
            { 2 : 2  }
    """
    _node_hash_user = {}


    def is_running(self, node):
        """
        @param node: node id
        @return: Boolean, true if the node running okay!
        else false return !
        """
        if node in self._node_hash_machine:
            machine = self._node_hash_machine[node]
            if machine in self._machine_hash_connect:
                return True
        return False


    def is_user_fillout_node(self, node):
        """
        @param node: node id
        @return : Boolean, true if the node has seat available
        else return False!
        """
        current_user_number = self._node_hash_user.get(node, 0)
        if current_user_number < self._node_max_user_number:
            return False
        else:
            return True


    def landing(self, room, user):
        """
        @param room: room id
        @param user: user id
        @return : node id, if no more node for use! return -1
        Usage:
            mmt.install_room(room, user)
        Example:
            {
                "ip": "127.0.0.1",
                "port":9001,
                "node":1,
                "room":2
            }
        """

        if room in self._room_hash_node:
            """
            if the target room has been install on some one node
            just search that node, return it!
            """
            node = self._room_hash_node[room]
            ip, port = self._node_hash_machine[node].split('-')
            self._user_hash_node[user]=node
            self._node_hash_user[node] = self._node_hash_user[node] + 1
            response = {"ip":ip, "port":port,
                        "node":node, "room":room}
            return response

        for node in self._node_hash_counter:
            if self.is_user_fillout_node(node):
                return -1
            else:

                self._room_hash_node[room] = node
                self._node_hash_room[node].append(room)
                self._node_hash_counter[node] = self._node_hash_counter[node]+1
                self._node_hash_user[node] = self._node_hash_user[node] + 1
                ip, port = self._node_hash_machine[node].split('-')
                self._user_hash_node[user]=node
                response = {"ip":ip, "port":port,
                        "node":node, "room":room}
                return response 


    def flying(self, uid):
        node = self._user_hash_node[uid]
        self._node_hash_user[node] = self._node_hash_user[node] - 1


    def recovery_data(self, data):
        """
        @param data: a dict-type
        Example:
                {
                    "command": "ack_recovery",      # command
                    'node': 2,                      # Node id
                    'user': 18,                     # user number
                    'rooms': [r1, r2, r3]           # room set
                    'counter': 64,                  # the total room in node
                    'machine':'127.0.0.1-9001'      # machine id
                }
        """
        node = data.get("node")
        user = data.get("user")
        rooms = data.get("rooms")
        counter = data.get("counter")
        machine = data.get("machine")
        
        self._node_hash_user[node] = user
        self._node_hash_counter[node] = counter
        for room in rooms:
            self._room_hash_node[room] = node

        
    def status(self):
        print '+' * 50
        print"_machine_hash_connect", self._machine_hash_connect
        print"_connect_hash_machine", self._connect_hash_machine
        print"_machine_hash_node", self._machine_hash_node
        print"_node_hash_room", self._node_hash_room
        print"_room_hash_node",  self._room_hash_node
        print"_node_hash_counter", self._node_hash_counter 
        print"_node_hash_user", self._node_hash_user
        print '+' * 50



if __name__ == '__main__':
 
#   mmt = NodeManager()
#    mmt.register('connect1', '127.0.0.1','9001')
#    mmt.register('connect2', '127.0.0.1','9002')
#    print mmt._machine_hash_connect 
#    print mmt._connect_hash_machine
#    print mmt._machine_hash_node
#    print mmt._node_hash_room
#    print mmt._room_hash_node 
#    print 'test unregister'
#    mmt.unregister('connect2')
#    mmt.register('connect2a', '127.0.0.1','9002')
#    print mmt._node_hash_room
    #=====================recovery test
    empty = NodeManager()
    empty.register('connect1', '127.0.0.1','9002', mode=2)
    #empty.recovery_connect('connect1a', '127.0.0.1','9002')
    sample_data = {
                    'node': 2,                      # Node id
                    'user': 18,                     # user number
                    'rooms': ['r1', 'r2', 'r3'],    # room set
                    'counter': 8,                  # the total room in node
                    'machine':'127.0.0.1-9002'      # machine id
                }
    empty.recovery_data(sample_data)
    empty.status()
                                                                                                                                                                                                                                                                                                                                                                                                                                    python-game-room/rserver/app/lib/room.py                                                            000644  000765  000024  00000020756 13015015762 021556  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         class _BaseRoomManager(object):
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
    @property _user_pending_status_set
    Usage: Only when the user has already connect to
    the WebSocket Server,and then that user will remove
    from this set!
    Example:
            {
                u1: 1,
                u1: ,
                u1: 0,
            }
    """
    _user_pending_status_set = set()
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
            self._room_hash_user_set[room_name].append(uid)
            self._user_hash_room[uid] = room_name
            self._user_counter = self._user_counter + 1
        else:
            # get new room
            self.new_room(uid)
        self._user_pending_status_set.add(uid)
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
                  python-game-room/rserver/app/lib/utils.py                                                           000644  000765  000024  00000002470 13015015762 021733  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         import logging
import time
import redis
import ujson


logger = logging.getLogger("rserver")

r = redis.Redis(host='127.0.0.1', port=6379)


def set_expire(key, ex=10):
    if isinstance(key, dict):
        str_key = ujson.dumps(key)
        r.set(str_key,1, ex=ex)
    else:
        r.set(key,1, ex=ex)


def is_expire(key):
    if isinstance(key, dict):
        key = ujson.dumps(key)
    value = r.get(key)
    if value == None:
        return True
    value = int(value)
    if  value == 0:
        return True
    else:
        return False


def mark_connected(key):
    if isinstance(key, dict):
        str_key = ujson.dumps(key)
        r.delete(str_key)
    else:
        r.delete(key)


def check_expire(manager):
    remove_list = []
    for uid in manager._user_pending_status_set:
        if is_expire(uid):
            logger.warning("User [%s] has expired" % uid)
            manager.check_out(uid)
            remove_list.append(uid)

    for uid in remove_list:
        remove_list.remove(uid)
        manager._user_pending_status_set.remove(uid)



if __name__ == '__main__':
    key = {"node":1,"room":2}
    key = 'hello jack'
    set_expire(key)
    print is_expire(key)
    time.sleep(3)    
    mark_connected(key)
    print is_expire(key)
    mark_connected(key)
    time.sleep(3)
    print is_expire(key)
    
                                                                                                                                                                                                        python-game-room/rserver/app/lib/views.py                                                           000644  000765  000024  00000002705 13015015762 021731  0                                                                                                    ustar 00landpack                        staff                           000000  000000                                                                                                                                                                         from core import DispatchCommand
from utils import is_expire , mark_connected
dc = DispatchCommand()



@dc.route("ping")
def ping(message, mmt, manager):
    #print 'I should sync data when ping coming recv ', message
    return {"command": "sync_all"}


@dc.route("ack_sync")
def ack_sync(message, mmt, manager):
    #print 'recv ', message
    #return {"command": "ack", "info":"sync success"}
    pass


@dc.route("check_in")
def check_in(message, mmt, manager):
    uid = message.get("uid")
    if uid in manager._user_pending_status_set:
        manager._user_pending_status_set.remove(uid)
        mark_connected(uid)
        return {"command":"ack_check_in", "status": "ok"}
    else:
        return {"command":"ack_check_in", "status": "bad"}
        

@dc.route("check_out")
def check_out(message, mmt, manager):
    uid = message.get("uid")
    if uid in manager._user_pending_status_set:
        return {"command":"ack_check_out", "status": "bad", "info":  "[Error] you have not check in!"}
    elif uid in manager._user_hash_room:
        #del key from redis
        manager.check_out(uid)
        mmt.flying(uid) #update _node_hash_user counter
        return {"command":"ack_check_out", "status": "ok"}
    else:
        return {"command":"ack_check_out", "status": "bad", "info": "you may has already check out"}

@dc.route("ack_recovery")
def ack_recovery(message, mmt, manager):
    mmt.recovery(message)
    return {"command":"ack_recovery", "status": "ok"}
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           