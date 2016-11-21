import logging

from core import DispatchCommand


dc = DispatchCommand()
logger = logging.getLogger("cserver")

global __connect_mode 

@dc.route("pong")
def pong(handler, request):
    data = {"command": "ping"}
    #handler.send(data)


@dc.route("connect")
def connect(handler, request):
    status = request.get("status")
    if status == 'ok':
        global __connect_mode
        __connect_mode = request.get("mode")
        if __connect_mode == 'recovery':
            logger.info('Reconnect successfully')
        else:
            logger.info('Connect successfully')
    else:
        pass


@dc.route("sync_all")
def sync_all(handler, request):
    data = {"command": "ack_sync"}
    handler.send(data)

@dc.route("close")
def close(handler, request):
    pass

@dc.route("ack_check_in")
def ack_check_in(handler, request):
    status = request.get("status")
    if status == "ok":
        # check in user local
        pass
    else:
        #TODO let the client know ~~~
        pass

@dc.route("ack_check_out")
def ack_check_out(handler, request):
    status = request.get("status")
    if status == "ok":
        #TODO do some clean job on local
        pass
    else:
        #TODO Don't need to let the client know ~~~
        pass

@dc.route("recovery")
def recovery(handler, request):
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
def ack_recovery(handler, request):
    print 'recovery success ..!'

