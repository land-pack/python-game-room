from views import WebSocketHandler
from views import JoinHandler
from views import MonitorHandler
from views import DashHandler
from views import CSVHandler


urls = [
    (r'/ws', WebSocketHandler),
    (r'/api/join', JoinHandler),
    (r'/monitor', MonitorHandler),
    (r'/dash', DashHandler),
    (r'/data.csv', CSVHandler),
]
