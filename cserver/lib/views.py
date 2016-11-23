import logging
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

