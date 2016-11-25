from tornado import ioloop
from tornado import web


class IndexHandler(web.RequestHandler):
    

    def get(self):
        """
            If client send many argument! but we don't care
            and then what will happen!
        """
        name = self.get_argument("name")
        age = self.get_argument("age")

        print name
        self.write("ok")

if __name__ == '__main__':
    application = web.Application([
            (r'/', IndexHandler),],
            debug=True)

    application.listen(9009)
    ioloop.IOLoop.instance().start()

