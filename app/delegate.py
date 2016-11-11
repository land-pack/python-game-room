from lib.websocket import RTCWebSocketClient
from tornado import ioloop
from tornado import websocket
from tornado import web
from tornado.options import options, define
from core import make_redirect
from room import RoomManager

define(name="port", default=9001, help="default port", type=int)
clients = []
manager = RoomManager()

io_loop = ioloop.IOLoop.instance()
token = RTCWebSocketClient(io_loop)
ws_url = 'ws://127.0.0.1:/ws'
client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)


class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    
    def open(self):
        clients[id(self)] = "anonymous"


    def on_close(self):
        clients.remove(self)
        user = clients[id(self)]
        msg = {"command": "check_out", "user": user}
        make_redirect(msg, token)


    def on_message(self, msg):
        response = make_redirect(msg, token)
        self.write_message(response)


def main():
    options.parse_command_line()
    application = web.Application([
        (r'/ws', WebSocketHandler),
        ],
        debug=True)
    application.listen(options.port)



    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
