from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.api.endpoints import index,user,task
from models import register_database
import logging
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        # 记录异常详细信息
        error_detail = {
            'timestamp': datetime.now().isoformat(),
            'path': request.url.path,
            'method': request.method,
            'error': str(exc),
            'traceback': traceback.format_exc()
        }
        
        # 写入日志
        logger.error(f"Request failed: {error_detail}")
        
        # 返回错误响应
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "success": False
            }
        )

# 假设你的静态文件存储在 "static" 文件夹中
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(index.router)
app.include_router(user.router)
app.include_router(task.router)

# 注册数据库
register_database()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app',host="0.0.0.0",port=8093, ssl_keyfile='./app/utils/jiancheng.asia.key',ssl_certfile='./app/utils/jiancheng.asia_bundle.pem')
    # uvicorn.run('main:app',host="0.0.0.0",port=8093)
    # uvicorn.run('main:app',host="0.0.0.0",port=80)