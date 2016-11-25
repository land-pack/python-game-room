import logging
from utils import is_expire, mark_connected

from system import RoomServer

rs = RoomServer()

logger = logging.getLogger("rserver")

"""
@rs.route("ping")
def ping(message):
    pass
    rs.to_do() ...
    rs.to_another() ...
"""


@rs.route("ping")
def ping(message):
    # print 'I should sync data when ping coming recv ', message
    return {"command": "sync_all"}


@rs.route("ack_sync")
def ack_sync(message):
    # print 'recv ', message
    # return {"command": "ack", "info":"sync success"}
    pass


@rs.route("ack_check_in")
def ack_check_in(message):
    uid = message.get("uid")
    if uid in rs._user_pending_status_set:
        rs._user_pending_status_set.remove(uid)
        mark_connected(uid)
        return {"command": "ack_check_in", "status": "ok"}
    else:
        return {"command": "ack_check_in", "status": "bad"}


@rs.route("ack_check_out")
def check_out(message):
    uid = message.get("uid")
    if uid in rs._user_pending_status_set:
        return {"command": "ack_check_out", "status": "bad", "info": "[Error] you have not check in!"}
    elif uid in rs._user_hash_room:
        # del key from redis
        rs.check_out(uid)
        rs.flying(uid)  # update _node_hash_user counter
        return {"command": "ack_check_out", "status": "ok"}
    else:
        return {"command": "ack_check_out", "status": "bad", "info": "you may has already check out"}


@rs.route("ack_recovery")
def ack_recovery(message):
    rs.recovery_room(message)
    return {"command": "ack_recovery", "status": "ok"}
