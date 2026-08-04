from data.models import SessionLocal, Conections

class Conections_repo:
    def __init__(self, db=None):
        if isinstance(db, str) or db is None:
            self.db = SessionLocal()
        else:
            self.db = db
    