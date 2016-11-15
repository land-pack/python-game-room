import os
import uuid
import websocket
import thread
import time
import ujson
import requests
import signal




clients = {}

def send_message():
    data = raw_input("Please input command:")
    


def on_message(ws, message):
    #data = ujson.loads(message)
    print 'from delegate>>',message
    #r = {"command": "ping", "uid": "frank"}
    if "chat_with" in message:
        #r = {"command": "ping", "uid": "frank"}
        #ws.send(ujson.dumps(r))
        print 'wait someone chat to me'
    else:
        req = ujson.dumps({"command": "chat_with", "to_uid":"jack", "content": "How do your do"})
        #ws.send(req)



def on_error(ws, error):
    print 'error', error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    print "### Open WebSocket ###"
    r = {"command": "ping", "uid": "frank"}
    ws.send(ujson.dumps(r))


if __name__ == "__main__":
    websocket.enableTrace(True)
#    uid = 'frank[%s]' % os.getpid()
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
    data = ujson.loads(data)
    if data == -1:
        print 'Currently no more node for use'
    else:
        ip = data['ip']
        port = data['port']
        node = data['node']
        room = data['room']
        print 'node[%s]---room[%s]' % (node, room) 
        """
        Connect to nginx / LB-Server --> delegate server
        """
        ws = websocket.WebSocketApp("ws://127.0.0.1:9000/ws?ip=%s&port=%s&node=%s&room=%s&uid=%s" % (ip, port, node, room, uid),
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()
