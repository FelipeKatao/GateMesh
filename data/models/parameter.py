from sqlalchemy import Column, Integer, String, Text
from data.models.base import Base

class Parameter(Base):
    __tablename__ = 'parameters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(50), default='system')  # 'system' or 'project'
    description = Column(Text, nullable=True)
