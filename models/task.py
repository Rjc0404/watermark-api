from sqlalchemy import Column, String, Boolean
from db.base import Base

class Task(Base):
    __tablename__ = "task"
    
    openid = Column(String(30), unique=True, nullable=False, primary_key=True)
    ad = Column(Boolean)
    ad2 = Column(Boolean)
    ad3 = Column(Boolean)
    share = Column(Boolean)
    share_circle = Column(Boolean)
    sign_date = Column(String(50))
    task_date = Column(String(5))