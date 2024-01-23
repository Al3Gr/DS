from flask import Flask, request, make_response
from slaDB import SlaDB
import os
import requests

app = Flask(__name__)
__db = SlaDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])
PROMETHEUS = "http://hub-prometheus-1:9090/"


@app.post("/create")
def create_sla():
    request_data = request.get_json()
    result = __db.create(request_data)
    if not result:
        return make_response("", 400)
    return make_response("", 200)


@app.get("/status")
def get_status():
    pass


@app.get("/status/metric")
def get_statusMetric():
    metrica = request.args.get("metrica")
    response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': metrica})
    result = response.json()['data']['result']
    make_response(result, 200)

@app.get("/violation")
def get_violation():
    pass


@app.get("/prevision")
def prevision():
    pass

if __name__ == "__main__":
    app.run()