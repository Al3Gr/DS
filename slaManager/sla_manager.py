from flask import Flask, request, make_response
from slaDB import SlaDB
import os
import prometheus_client

app = Flask(__name__)
__db = SlaDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])


@app.post("/create")
def create_sla():
    pass

@app.get("/status")
def get_status():
    pass


@app.get("/violation")
def get_violation():
    pass


@app.get("/prevision")
def prevision():
    pass

if __name__ == "__main__":
    app.run()