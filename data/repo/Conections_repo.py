from data.models import SessionLocal, Conections

class Conections_repo:
    def __init__(self, db=None):
        if isinstance(db, str) or db is None:
            self.db = SessionLocal()
        else:
            self.db = db

    def get_all(self):
        return self.db.query(Conections).all()

    def CreateNewCon(self,ip,port,service):
        conections = Conections(ip=ip,port=port,Service=service)
        self.db.add(conections)
        self.db.commit()
