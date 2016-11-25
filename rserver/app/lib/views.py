import logging
from core import DispatchCommand
from utils import is_expire, mark_connected

dc = DispatchCommand()

logger = logging.getLogger("rserver")

"""
@rs.route("ping")
def ping(message):
    pass
    rs.to_do() ...
    rs.to_another() ...
"""


@dc.route("ping")
def ping(message, mmt, manager):
    # print 'I should sync data when ping coming recv ', message
    return {"command": "sync_all"}


@dc.route("ack_sync")
def ack_sync(message, mmt, manager):
    # print 'recv ', message
    # return {"command": "ack", "info":"sync success"}
    pass


@dc.route("ack_check_in")
def ack_check_in(message, mmt, manager):
    uid = message.get("uid")
    if uid in manager._user_pending_status_set:
        manager._user_pending_status_set.remove(uid)
        mark_connected(uid)
        return {"command": "ack_check_in", "status": "ok"}
    else:
        return {"command": "ack_check_in", "status": "bad"}


@dc.route("ack_check_out")
def check_out(message, mmt, manager):
    uid = message.get("uid")
    if uid in manager._user_pending_status_set:
        return {"command": "ack_check_out", "status": "bad", "info": "[Error] you have not check in!"}
    elif uid in manager._user_hash_room:
        # del key from redis
        manager.check_out(uid)
        mmt.flying(uid)  # update _node_hash_user counter
        return {"command": "ack_check_out", "status": "ok"}
    else:
        return {"command": "ack_check_out", "status": "bad", "info": "you may has already check out"}


@dc.route("ack_recovery")
def ack_recovery(message, mmt, manager):
    mmt.recovery_room(message)
    return {"command": "ack_recovery", "status": "ok"}
