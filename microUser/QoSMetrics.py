from prometheus_client import start_http_server, Counter

class QoSMetrics:
    def __init__(self):
        start_http_server(9000)

        self.logged_user_counter = Counter('sessions_count', 'Number of users logged or registred') 

    def userLogged(self, login_type):
        self.logged_user_counter.inc()