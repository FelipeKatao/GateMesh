import datetime
import os
import yaml
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, g
from GateMonitor_package.GateMonitorHttp import GateMonitorHttp
from data.repo.logs_repo import Logs_repo
import requests, time

Api_GateMesh = Blueprint('api', __name__)
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = f"config\\gateway.yml"

@Api_GateMesh.route('/base', methods=['GET'])
def index():
    return {"Call_service": "Redirecionado por Limit"}

@Api_GateMesh.route('/_gateway/service/<service>', methods=['GET'])
def gateway_config(service):    
    LogRepo = Logs_repo()
    with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            request.get_data
            for i in config["routes"]:
                if i["name"] == service:
                    data = request.get_json()
                    data["target"] = i["target"]
                    GateMonitor = GateMonitorHttp(data)
                    tokenSerrver =GateMonitor.GetToken(data.get("app"))
                    if tokenSerrver is not None and tokenSerrver[0] != data.get("token"):
                        return {"Call_service": "Acess denied"}
                    if data.get("config_register") is not None:
                         GateMonitor.CreateConfigsToServer(data["config_register"],data["app"])
                         return {"Call_service": "Config register"}
                    if os.path.exists(f"config\\{data['app']}.gmc"):
                         with open(f"config\\{data['app']}.gmc", "r") as f:
                             data_ = f.read()
                    start = time.perf_counter()
                    RespondeData = GateMonitor.ExecuteGmcFile(data_)
                    elapsed = time.perf_counter() - start
                    size_bytes = len(RespondeData.content)
                    size_mb = size_bytes / (1024 * 1024)
                    timestamp = datetime.datetime.now()
                    Alert = classify_http_status(RespondeData.status_code)
                    if isinstance(RespondeData, dict):
                        LogRepo.CreateNewLog(timestamp,RespondeData.text,RespondeData.status_code,Alert,data["app"],RespondeData.url,elapsed,size_mb)
                        return {"Call_service": RespondeData}
                    if RespondeData.status_code == 404:
                        LogRepo.CreateNewLog(timestamp,RespondeData.text,RespondeData.status_code,Alert,data["app"],RespondeData.url,elapsed,size_mb)
                        return {"Call_service": "Service dont exist"}
                    LogRepo.CreateNewLog(timestamp,RespondeData.text,RespondeData.status_code,Alert,data["app"],RespondeData.url,elapsed,size_mb)
                    return {"Call_service": RespondeData.json()}
                     
    return {"Call_service": "Service dont exist"}

def classify_http_status(status_code: int) -> str:
    """
    Classifica o status HTTP em categorias:
    - 2xx → Ok
    - 3xx → Warning (redirecionamentos)
    - 4xx → Erro (cliente)
    - 5xx → Crítico (servidor)
    """
    if 200 <= status_code < 300:
        return "Ok"
    elif 300 <= status_code < 400:
        return "Warning"
    elif 400 <= status_code < 500:
        return "Erro"
    elif 500 <= status_code < 600:
        return "Crítico"
    else:
        return "Desconhecido"