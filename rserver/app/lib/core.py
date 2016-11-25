import ujson


class DispatchCommand(object):
    _command_hash_views = {}

    def route(self, command):
        def _route(func):
            self._command_hash_views[command] = func

            def __route(*args, **kwargs):
                return func(*args, **kwargs)

            return _route

        return _route

    def render(self, message):
        data = ujson.loads(message)
        command = data.get("command")
        if command in self._command_hash_views:
            data = self._command_hash_views[command](data)
        else:
            data = {"command": "nothing"}
        if data:
            response = ujson.dumps(data)
            return response


if __name__ == '__main__':
    dc = DispatchCommand()


    @dc.route("add")
    def add(handler, data):
        print 'i am add', data


    @dc.route("sub")
    def add(handler, data):
        print 'i am sub', data


    message = ujson.dumps({"command": "xxsub", "someting": "aaa"})
    dc.dispatch(None, message)
