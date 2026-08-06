from data.models.base import Base
from sqlalchemy import Column, DateTime, Integer, String, Text

class Logs(Base):
    __tablename__ = 'logs_connections'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    ResposeHttp = Column(Integer, nullable=False)
    Alert = Column(String(100), nullable=False)
    service = Column(String(100), nullable=False)
    RouteRequest = Column(String(100), nullable=False)
    Time = Column(String(100), nullable=False)
    MemoryCoast = Column(String(100), nullable=False)