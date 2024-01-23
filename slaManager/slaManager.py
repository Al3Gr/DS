from flask import Flask, request, make_response
from slaDB import SlaDB
import os
import time
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
    slos = __db.getSLOS()
    
    dictionary = {}

    for slo in slos:
        nomeMetrica = slo["_id"]
        min = slo["min"]
        max = slo["max"]
        
        if("aggregation" in slo):
            aggregation = slo["aggregation"]
            aggregationTime = slo["aggregationtime"]
            match aggregation:
                case ["increase"]:
                    query = "increase("+nomeMetrica+"["+ aggregationTime +"])"
                case ["sum"]:
                    query = "sum_over_time("+nomeMetrica+"["+ aggregationTime +"])"
                case ["avg"]:
                    query = "avg_over_time("+nomeMetrica+"["+ aggregationTime +"])"
        else:
            query = nomeMetrica

        response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': query})
        result = response.json()['data']['result']
        if (result < min or result > max):
            dictionary[nomeMetrica] = False
        else:
            dictionary[nomeMetrica] = True

    return make_response(dictionary, 200)

        


@app.get("/status/metric")
def get_statusMetric():
    metrica = request.args.get("metrica")
    response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': metrica})
    result = response.json()['data']['result']
    return make_response(result, 200)

@app.get("/violation")
def get_violation():
    #range vector

    pass


@app.get("/prevision")
def prevision():
    pass

if __name__ == "__main__":
    app.run()