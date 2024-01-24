from flask import Flask, request, make_response
from slaDB import SlaDB
import os
import time
import requests
import pandas as pd

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
        min = float(slo["min"])
        max = float(slo["max"])
        
        if("aggregation" in slo):
            aggregation = slo["aggregation"]
            aggregationTime = slo["aggregationtime"]
            match aggregation:
                case "increase":
                    query = "increase("+nomeMetrica+"["+ aggregationTime +"])"
                case "sum":
                    query = "sum_over_time("+nomeMetrica+"["+ aggregationTime +"])"
                case "avg":
                    query = "avg_over_time("+nomeMetrica+"["+ aggregationTime +"])"
        else:
            query = nomeMetrica

        response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': query})
        result = float(response.json()['data']['result'][0]['value'][1])
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
    seconds = int(request.args.get("seconds")) #1h = 3600

    slos = __db.getSLOS()
    
    dictionary = {}

    for slo in slos:
        nomeMetrica = slo["_id"]
        min = float(slo["min"])
        max = float(slo["max"])

        response = requests.get(PROMETHEUS + '/api/v1/query_range', params={'query': nomeMetrica, 'start': time.time()-seconds, 'end': time.time(), 'step': '15s'})
        result = response.json()['data']['result'][0]['values'] #è una lista dove ogni elemento è una list il cui primo elemento è il timestamp e il secondo è il valore

        #convertire il risultato in DataFrame di pandas
        df = pd.DataFrame(result, columns=['Time', 'Value'])
        df.set_index('Time')
        df['Time'] = pd.to_datetime(df['Time'], unit='s')

        if("aggregation" in slo):
            aggregation = slo["aggregation"]
            aggregationTime = slo["aggregationtime"]
            match aggregation:
                case "increase":
                    tmax = df.rolling(aggregationTime).max()
                    tmin = df.rolling(aggregationTime).min()
                    df = tmax - tmin
                case "sum":
                    df = df.rolling(aggregationTime).sum()
                case "avg":
                    df = df.rolling(aggregationTime).mean()

        dictionary[nomeMetrica] = 0
        for _, row in df.iterrows():
            val = row[df.columns[0]]
            if (val < min or val > max):
                dictionary[nomeMetrica] += 1

    return make_response(dictionary, 200)


@app.get("/prevision")
def prevision():
    pass

if __name__ == "__main__":
    app.run()