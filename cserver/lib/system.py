import socket
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


