import os
import uuid
import websocket
import thread
import time
import ujson
import requests





clients = {}

def on_message(ws, message):
    #data = ujson.loads(message)
    print data


def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    print 'open websocket'
    sample = {
            "type": "command",
            "command": "check_in",
            "user": "Frank %s" % os.getpid()
        }
    request = ujson.dumps(sample)
    print "### Open WebSocket ###"
    ws.send(request)


if __name__ == "__main__":
    websocket.enableTrace(True)
    user = 'frank'
    response = requests.get('http://127.0.0.1:8888/api/join?user=%s' % user)
    """
    {
        "ip":"xxxxxxxxxxyyyy",
        "port":"8899",
        "node":1,
        "room":"room1"
    }
    """
    data = response.content
    data = ujson.loads(data)
    ip = data.get("ip")
    port = data.get("port")
    node = data.get("node")
    room = data.get("room")
    print 'node', node
    print 'room', room
    """
    Connect to nginx / LB-Server --> delegate server
    """
    ws = websocket.WebSocketApp("ws://127.0.0.1:8880/ws?ip=%s&port=%s&node=%s&room=%s&user=%s" % (ip, port, node, room, user),
    on_message = on_message,
    on_error = on_error,
    on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
