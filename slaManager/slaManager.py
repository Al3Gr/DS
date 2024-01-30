from flask import Flask, request, make_response
from slaDB import SlaDB
import forecast
import os
import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
__db = SlaDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])
PROMETHEUS = os.environ["prometheus_server"]


@app.post("/create")
def create_sla():
    request_data = request.get_json()
    result = __db.create(request_data)
    if not result:
        return make_response("", 400)
    
    df = downloadTimeSerie(request_data, 604800, "2m")
    forecastObject = forecast.forecast(request_data["_id"],df)
    with ThreadPoolExecutor() as executor:
        executor.submit(forecastObject.trainModel)

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
                case "median":
                    query = "quantile_over_time(0.5, "+nomeMetrica+"["+ aggregationTime +"])"
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

        df= downloadTimeSerie(slo, seconds, "15s")

        dictionary[nomeMetrica] = 0
        for _, row in df.iterrows():
            val = row[df.columns[0]]
            if (val < min or val > max):
                dictionary[nomeMetrica] += 1

    return make_response(dictionary, 200)

def windowRollingTimeSerie(df, aggregation, aggregationTime):
    match aggregation:
        case "median":
            df = df.rolling(aggregationTime).median()
        case "increase":
            tmax = df.rolling(aggregationTime).max()
            tmin = df.rolling(aggregationTime).min()
            df = tmax - tmin
        case "sum":
            df = df.rolling(aggregationTime).sum()
        case "avg":
            df = df.rolling(aggregationTime).mean()
    return df

def downloadTimeSerie(slo, seconds, steps):
    response = requests.get(PROMETHEUS + '/api/v1/query_range', params={'query': slo['_id'], 'start': time.time()-seconds, 'end': time.time(), 'step': steps})
    result = response.json()['data']['result'][0]['values'] #è una lista dove ogni elemento è una list il cui primo elemento è il timestamp e il secondo è il valore

    #convertire il risultato in DataFrame di pandas
    df = pd.DataFrame(result, columns=['Time', 'Value'])
    df['Time'] = pd.to_datetime(df['Time'], unit='s')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.set_index('Time')

    if("aggregation" in slo):
        df = windowRollingTimeSerie(df, slo["aggregation"], slo["aggregationtime"])

@app.get("/prevision")
def prevision():
    #secondi presi nel passato per fare la previsione sul futuro
    seconds = 604800 #3600*24*7=3h
    #durata in secondi della previsione nel futuro
    futureMinutes = int(request.args.get("minutes"))

    slos = __db.getSLOS()

    #dictionary con nome metrica e probabilità di violazione    
    dictionary = {}

    for slo in slos:
        nomeMetrica = slo["_id"]
        min = float(slo["min"])
        max = float(slo["max"])

        df= downloadTimeSerie(slo, seconds, "2m")

        #qui generare la previsione e l'intervallo
        confInt = forecast.forecast(nomeMetrica, df).get_ConfInt(futureMinutes)
        if confInt is None:
            return make_response("Too few data to converge!", 200)
        lowInt = confInt["lower Value"]
        upInt = confInt["upper Value"]

        #qui vedere il massimo della probabilità
        umax = upInt.max()
        lmax = lowInt.max()
        umin = upInt.min()
        lmin = lowInt.min()
        distanzasup = umax-lmax
        distanzainf = umin-lmin
        psup = 0
        if umax > max:
            psup += (umax-max)/distanzasup
        if lmax < min:
            psup += (min-lmax)/distanzasup
        pinf = 0 
        if umin > max:
            pinf += (umin-max)/distanzainf
        if lmin < min:
            pinf += (min-lmin)/distanzainf

        dictionary[nomeMetrica] = min(max(psup, pinf), 1)

    return make_response(dictionary, 200)

if __name__ == "__main__":
    app.run()