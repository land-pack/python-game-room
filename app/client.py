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
    print 'from delegate>>',message



def on_error(ws, error):
    print 'error', error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    print "### Open WebSocket ###"
    r = {"user": "frank"}
    ws.send(ujson.dumps(r))


if __name__ == "__main__":
    websocket.enableTrace(True)
    user = 'frank'
    response = requests.get('http://127.0.0.1:8888/api/join?user=%s' % user)
    """
    {
        "ip":"xxxxxxxxxxyyyy",
        "port":"8899",
        "node":1,
    }
    """
    data = response.content
    data = ujson.loads(data)
    if data == -1:
        print 'Currently no more node for use'
    else:
        ip = data['ip']
        port = data['port']
        node = data['node']
        """
        Connect to nginx / LB-Server --> delegate server
        """
        ws = websocket.WebSocketApp("ws://127.0.0.1:9000/ws?ip=%s&port=%s&node=%s&user=%s" % (ip, port, node, user),
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()
