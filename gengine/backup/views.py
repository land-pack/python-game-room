from core import DispatchCommand


dc = DispatchCommand()


@dc.route("ping")
def ping(handler, data):
    data = {"status": 200, "info":"pong"}
    ws.send(data)


@dc.route("add_user")
def add_user(handler, data):
    data = {"status": 200, "info":"add new user"}
    handler.send(data)


@dc.route("sync")
def sync(handler, data):
    data = {"status": 200, "info":"sync successfully"}
    handler.send(data)
