from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import index,user,task
from models import register_database
app = FastAPI()

# 假设你的静态文件存储在 "static" 文件夹中
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(index.router)
app.include_router(user.router)
app.include_router(task.router)

# 注册数据库
register_database()

if __name__ == '__main__':
    import uvicorn
    # uvicorn.run('main:app',host="0.0.0.0",port=8093, ssl_keyfile='./app/utils/jiancheng.asia.key',ssl_certfile='./app/utils/jiancheng.asia_bundle.pem')
    uvicorn.run('main:app',host="0.0.0.0",port=8093)