import time
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
    msg = {'command': 'msg', 'from': 'Frankie',
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
        data = ujson.loads(msg)
        if 'node_id' in data:
            self.node_id= data.get("node_id")
        else:
            pass

    def on_connection_success(self):
        print('Connected!')
        self.send(self.msg)
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


def main():
    io_loop = ioloop.IOLoop.instance()

    client = RTCWebSocketClient(io_loop)
    #ws_url = 'ws://127.0.0.1:8090/ws'
    ws_url = 'ws://echo.websocket.org'
    client.connect(ws_url, auto_reconnet=True, reconnet_interval=10)

    try:
        io_loop.start()
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    main()
