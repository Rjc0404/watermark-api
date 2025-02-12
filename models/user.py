from sqlalchemy import Column, Integer, String, Text
from db.base import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    openid = Column(String(30), unique=True, nullable=False)
    score = Column(Integer)
    nickname = Column(String(20))
    avatar = Column(Text)