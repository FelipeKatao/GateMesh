from data.models import SessionLocal, Parameter

class ParansRepo:
    def __init__(self, db=None):
        if isinstance(db, str) or db is None:
            self.db = SessionLocal()
        else:
            self.db = db

    def get_all(self):
        return self.db.query(Parameter).all()

    def get_by_name(self, name):
        return self.db.query(Parameter.value).filter(Parameter.key == name).first()