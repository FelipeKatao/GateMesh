from flask import Flask
from GateMonitor.monitor import Monitor
from GateMonitor_package.GateMonitorHttp import GateMonitorHttp
from data.models import init_db


class GateMonitor:
    def __init__(self,host,port=5000):
        self.gateMonitorHttp = GateMonitorHttp(host,port)

    def start(self):
        # Initialize database tables and default admin user
        init_db()
        
        app = Flask(__name__)
        app.secret_key = 'gatemesh-monitor-secret-key-change-me'
        app.register_blueprint(Monitor)
        app.run(debug=True,port=self.gateMonitorHttp.port)
        return app