import socket
import logging
import ujson
from tornado import ioloop
from websocket import RTCWebSocketClient
from machine import MachineManager

logger = logging.getLogger("cserver")

class LocalSystem(RTCWebSocketClient, MachineManager):
    """
    LocalSystem
    Combine two core thing! 1, the websocket client side implement on tornado!
    2, Machine / Basic data manager!
    """
    _command_hash_views = {}


    def route(self, command):
        """
        The route method as it's name implicate, we can route the message to
        their own view function. how do we use it?
        Example:
            @local_system.route("connect")
            def connect(handler, data):
                data = to_do(data)
                handler.send(data)

        Args:
            command:

        Returns:

        """

        def _route(func):
            self._command_hash_views[command] = func

            def __route(*args, **kwargs):
                return func(*args, **kwargs)

            return __route

        return _route

    def dispatch(self, message):
        """
        The message can be anything, but always format like `Example` show,
        this method will dispatch each message to they own home view function!
        Once the websocket connect success, the first message will receive from
        room server. the `command` field should be filled with `connect`. if everything
        goes right! the `connect` function will trigger, and then time to work with
        `MachineManager` which inside property `check_in` will be called. Cause we need
        to process `ip-port` hash to `node`.

        Args:
            message: a string type, from room server side!
            Example '{"command": "connect", "status": "ok"}'
        Returns:
            None
        """
        data = ujson.loads(message)
        print  '....///',data
        command = data.get("command", "no command field!")
        if command in self._command_hash_views:
            self._command_hash_views[command](self, data)
        else:
            # handler.send("404 Error")
            logger.warning("Sorry! System don't understand command[%s]" % command)

    def run(self, rsp=8888, port=9001):
        """
        Args:
            rsp: The room server listen port
            port: The current machine listen port
        Returns:
            None
        """
        ip = socket.gethostbyname(socket.gethostname())
        url_template = 'ws://127.0.0.1:%s/ws?ip=%s&port=%s' % (rsp, ip, port)
        ws_url = url_template + "&node=%s"
        self.connect(ws_url, auto_reconnet=True, reconnet_interval=10)


if __name__ == '__main__':
    local_system = LocalSystem()
    local_system.run()
    io_loop = ioloop.IOLoop.current().instance()
    io_loop.start()
