from core import TalkManager

tm = TalkManager()



@tm.route("ping")
def ping(message, lm):
    return {"command": "pong"}


@tm.route("chat_with")
def chat_with(message, lm):
    """
    @param message: a dict-type
        {   
            "command": "chat_with",
            "content": "hello another guys",
            "to_uid": "xxxxx"
        }
    """
    print "recv a chat with command"
    to_uid = message.get("to_uid")
    from_uid = message.get("from_uid")
    message = "hello "
    response = lm.chat_with(from_uid, to_uid, message)
    if response:
        return {"command":"chat_with", "status":"ok"}
    else:
        return {"command": "chat_with", "status":"bad","info":"no such user"}

@tm.route("broadcast")
def broadcast(message, lm):
    pass

