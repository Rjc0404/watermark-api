from db.base import engine,Base

def register_database():
    # 预先创建数据表
    from . import user, task

    Base.metadata.create_all(bind=engine)