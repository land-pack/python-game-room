from system import local_system


@local_system.route("connect")
def connect(handler, data):
    node = data.get("node")
    handler.set_node(node)
    response = {"command": " ack_connect"}
    handler.send(response)


@local_system.route("reconnect")
def reconnect(handler, data):
    data = handler.help_recovery()
    handler.send(data)


