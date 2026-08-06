import os
import yaml
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, g
from GateMonitor_package.GateMonitorHttp import GateMonitorHttp


Api_GateMesh = Blueprint('api', __name__)
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = f"config\\gateway.yml"

@Api_GateMesh.route('/base', methods=['GET'])
def index():
    return {"Call_service": "Redirecionado por Limit"}

@Api_GateMesh.route('/_gateway/service/<service>', methods=['GET'])
def gateway_config(service):    
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
                    RespondeData = GateMonitor.ExecuteGmcFile(data_)
                    if isinstance(RespondeData, dict):
                         return {"Call_service": RespondeData}
                    if RespondeData.status_code == 404:
                         return {"Call_service": "Service dont exist"}
                    print(RespondeData)
                    return {"Call_service": RespondeData.json()}
                     
    return {"Call_service": "Service dont exist"}