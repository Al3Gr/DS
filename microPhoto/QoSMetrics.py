from prometheus_client import start_http_server, Counter, Gauge

class QoSMetrics:
    def __init__(self):
        start_http_server(9000)

        self.image_size = Gauge('image_size', 'Number of bytes of the image')
        self.upload_time = Gauge("upload_image_time", "Time elapsed for each upload")
        self.total_time = Gauge("upload_and_tag_time", "Time elapsed to complete the upload&tag procedure")

    def setImageSize(self, size):
        self.image_size.set(size)
    
    def setUploadTime(self, time):
        self.upload_time.set(time)

    def setTotalTime(self, time):
        self.total_time.set(time)