from core import DispatchCommand
from utils import is_expire , mark_connected
dc = DispatchCommand()



@dc.route("ping")
def ping(message, mmt, manager):
    #print 'I should sync data when ping coming recv ', message
    return {"command": "sync_all"}


@dc.route("ack_sync")
def ack_sync(message, mmt, manager):
    #print 'recv ', message
    #return {"command": "ack", "info":"sync success"}
    pass


@dc.route("check_in")
def check_in(message, mmt, manager):
    uid = message.get("uid")
    if uid in manager._user_pending_status_set:
        manager._user_pending_status_set.remove(uid)
        mark_connected(uid)
        return {"command":"ack_check_in", "status": "ok"}
    else:
        return {"command":"ack_check_in", "status": "bad"}
        

@dc.route("check_out")
def check_out(message, mmt, manager):
    uid = message.get("uid")
    if uid in manager._user_pending_status_set:
        return {"command":"ack_check_out", "status": "bad", "info":  "[Error] you have not check in!"}
    elif uid in manager._user_hash_room:
        print ' can i got there'
        #del key from redis
        manager.check_out(uid)
        mmt.flying(uid) #update _node_hash_user counter
        return {"command":"ack_check_out", "status": "ok"}
    else:
        return {"command":"ack_check_out", "status": "bad", "info": "you may has already check out"}
