from prometheus_client import start_http_server, Counter, Gauge

class QoSMetrics:
    def __init__(self):
        start_http_server(9000)

        self.image_size = Gauge('image_size', 'Number of bytes of the image')

    def setImageSize(self, size):
        self.image_size.set(size)