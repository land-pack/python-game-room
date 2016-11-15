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

class DispatchCommand(object):
    
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route

    
    def dispatch(self, handler, message):
        data = ujson.loads(message)
        command = data.get("command")
        if command in self._command_hash_views:
            self._command_hash_views[command](handler, data)
        else:
           #handler.send("404 Error")
            print "404--Can't parser command[%s]" % command
            print "data complete is [%s]", data

   
    def render(self, message, mmt):
        data = ujson.loads(message)
        command = data.get("command")
        if command in self._command_hash_views_function:
            data = self._command_hash_views[command](data, mmt)
            
        else:
            data = {"command":"nothing"}
        response = ujson.dumps(data)
        return response
        

if __name__ == '__main__':
    dc = DispatchCommand()
    @dc.route("add")
    def add(handler, data):
        print 'i am add',data
    
    @dc.route("sub")
    def add(handler, data):
        print 'i am sub', data


    message = ujson.dumps({"command":"xxsub","someting":"aaa"})
    dc.dispatch(None, message)
