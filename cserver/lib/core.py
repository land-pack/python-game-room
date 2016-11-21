import ujson

class ConnectMode(object):
    _mode_choice = ['normally', 'recovery']
    def __init__(self):
        self.index = 0
    
    @property
    def mode(self):
        ret = self._mode_choice[self.index]
        self.index = 1
        return ret


class DispatchCommand(object):
    
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route

    
    def dispatch(self, handler, message ):
        data = ujson.loads(message)
        command = data.get("command")
        if command in self._command_hash_views:
            self._command_hash_views[command](handler, data)
        else:
           #handler.send("404 Error")
            print "404--Can't parser command[%s]" % command
            print "data complete is [%s]" % data
   


class TalkManager(object):
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func
            def __route(*args, **kwargs):
                return func(*args, **kwargs)
            return _route
        return _route
    
   
    def render(self, message, mmt):
        data = ujson.loads(message)
        print '>>>>>>>>>>>>', data
        command = data.get("command")
        if command in self._command_hash_views:
            data = self._command_hash_views[command](data, mmt)
        else:
            data = {"command":"nothing"}

        if data:
            response = ujson.dumps(data)
            return response
        else:
            return None
        
