from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:!Rjc15198238500@localhost:3306/watermark?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
)

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
Base = declarative_base()