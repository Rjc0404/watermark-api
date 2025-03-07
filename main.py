from fastapi import FastAPI, Request
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

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     response = await call_next(request)
#     if 'static' in request.url.path or 'login' in request.url.path:
#         return response
#     if 'jwt' not in request.headers:
#         return {'success': False, 'msg': '用户不存在'}
#     user = db.query(User).filter_by(openid=request.headers['jwt']).first()
#     if not user:
#         return {'success': False, 'msg': '用户不存在'}
    
#     return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app',host="0.0.0.0",port=8093, ssl_keyfile='./app/utils/jiancheng.asia.key',ssl_certfile='./app/utils/jiancheng.asia_bundle.pem')
    # uvicorn.run('main:app',host="0.0.0.0",port=8093)
    # uvicorn.run('main:app',host="0.0.0.0",port=80)