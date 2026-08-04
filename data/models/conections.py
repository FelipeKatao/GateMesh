from sqlalchemy import Column, Integer, String, Text
from data.models.base import Base


class Conections(Base):
    __tablename__ = 'conections'
    id = Column(Integer, primary_key=True)
    ip = Column(String(50), nullable=False)
    port = Column(Integer, nullable=False)
    Service = Column(String(50), nullable=False)