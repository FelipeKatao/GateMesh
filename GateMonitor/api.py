import os
import yaml
import urllib.request
import urllib.error
from pathlib import Path
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, g
from data.models import SessionLocal, User, Parameter
from functools import wraps

Api_GateMesh = Blueprint('api', __name__)
BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = f"config\\gateway.yml"

@Api_GateMesh.route('/_gateway/service/<service>', methods=['GET'])
def gateway_config(service):    
    with open(CONFIG_FILE, "r") as f:
            config = yaml.safe_load(f)
            for i in config["routes"]:
                if i["name"] == service:
                   return {"Call_service": service}
    return {"Call_service": "Service dont exist"}
