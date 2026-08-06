from data.models import SessionLocal, Conections
from data.models.logs import Logs

class Logs_repo:
    def __init__(self, db=None):
        self.Logs_model = Logs()
        if isinstance(db, str) or db is None:
            self.db = SessionLocal()
        else:
            self.db = db

    def CreateNewLog(self, timestamp, message, ResposeHttp, Alert, service, RouteRequest, Time, MemoryCoast):
        self.Logs_model.timestamp = timestamp
        self.Logs_model.message = message
        self.Logs_model.ResposeHttp = ResposeHttp
        self.Logs_model.Alert = Alert
        self.Logs_model.service = service
        self.Logs_model.RouteRequest = RouteRequest
        self.Logs_model.Time = Time
        self.Logs_model.MemoryCoast = MemoryCoast
        self.db.add(self.Logs_model)
        self.db.commit()
        self.db.close()

        return self.Logs_model
