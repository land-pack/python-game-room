import os
import logging
import logging.config
from tornado.options import options, define
from tornado import web
from tornado import ioloop
from app.url import urls
from app.lib import color
from app.lib.utils import check_expire 
from app.views import manager 


logging.config.fileConfig("log.conf")
logger = logging.getLogger("rserver")

define(name="port", default=8888, help="default port", type=int)

if __name__ == '__main__':
    options.parse_command_line()
    application = web.Application(
                urls,
                debug=True,
                template_path=os.path.join(os.path.dirname(__name__),'app/templates'))

    logger.info('Listen on %s' %  options.port)
    application.listen(options.port)
    ioloop.PeriodicCallback(lambda :check_expire(manager) , 1000).start()
    ioloop.IOLoop.instance().start()
