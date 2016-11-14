import ujson


def make_response(msg, mmt):
    """
    @param msg: message from delegate on websocket 
    @param mmt: instance of NodeManager
    @return : a string
    """
    data = ujson.loads(msg)
    m_command = data.get("command")

    if m_command == 'add_user':
        pass
    elif m_command == 'del_user':
        user= daya.get("user")
        mmt.del_user(user)
    elif m_command == 'ping':
        data = {"status": 200, "info":"pong"}
    else:
        data = {"status": 200, "info":"invalid command"}
    response = ujson.dumps(data)
    return response 
