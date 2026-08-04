import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models.base import Base

# Path to database in the project root directory
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'gatemesh.db'))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from data.models.user import User
        if db.query(User).count() == 0:
            admin = User(username='admin')
            admin.set_password('admin')
            db.add(admin)
            db.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
