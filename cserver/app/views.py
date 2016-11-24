import logging
from system import LocalSystem
local_system = LocalSystem()


logger = logging.getLogger("cserver")

@local_system.route("connect")
def connect(handler, data):
    logger.info("Register sucess with node [%s]" % data.get("node"))
    node = data.get("node")
    handler.set_node(node)
    response = {"command": " ack_connect"}
    handler.send(response)


@local_system.route("recovery")
def recovery(handler, data):
    data = handler.help_recovery()
    handler.send(data)

@local_system.route("sync_all")
def sync_all(handler, data):
    logger.info("[Sync] data to room server")


@local_system.route("check_in")
def check_in(handler, data):
    logger.info("[In] One user has join")
