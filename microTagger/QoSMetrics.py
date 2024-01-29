from prometheus_client import start_http_server, Counter, Gauge

class QoSMetrics:
    def __init__(self):
        start_http_server(9000)

        self.inference_counter = Counter('inference_count', 'Number of inference performed')
        self.inference_time = Gauge("inference_time", "Time elapsed for each inference")

    def setInferenceInfo(self, photo_tag, time):
        self.inference_counter.inc()
        self.inference_time.set(time)