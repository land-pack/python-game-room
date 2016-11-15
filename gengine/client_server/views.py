from core import DispatchCommand
dc = DispatchCommand()


@dc.route("pong")
def pong(handler, request):
    data = {"command": "ping"}
    #handler.send(data)


@dc.route("connect")
def add_user(handler, request):
    #data = {"command": ""}
    #handler.send(data)
    print 'connect successfully'


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
        pass
    else:
        #TODO let the client know ~~~
        pass

@dc.route("ack_check_out")
def ack_check_out(handler, request):
    status = request.get("status")
    if status == "ok":
        pass
    else:
        #TODO let the client know ~~~
        pass
