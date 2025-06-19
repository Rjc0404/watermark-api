import requests
from fastapi import APIRouter, Header, UploadFile, File
from db.base import db
from models.user import User
from models.task import Task
import aiofiles

router = APIRouter()

@router.get("/api/login")
def login(code):
    response = requests.get("https://api.weixin.qq.com/sns/jscode2session?appid=wx5bb2b38dcb169957&secret=4bcbe7130c538dda3864b49bf9f1b8c9&grant_type=authorization_code&js_code=" + code)
    res = response.json()
    try:
        user=db.query(User).filter_by(openid=res['openid']).first()
        if not user:
            newUser = User(openid=res['openid'], score=6, nickname='给自己设置个昵称吧~', avatar='')
            newTask = Task(
            openid=res['openid'],
            ad=False,
            share=False,
            share_circle=False,
            sign_date='',
            task_date='',
            share_count=0,
            )
            db.add(newUser)
            db.add(newTask)

            db.commit()
    except:
        db.rollback()
    finally:
        db.close()

    return {
        "success": True,
        'openid': res['openid']
    }

@router.get("/api/findUserInfo")
def findUserInfo(jwt: str = Header(None)):
    try:
        user = db.query(User).filter_by(openid=jwt).first()
        if not user:
            return {'success': False, 'msg': '用户不存在'}
        return {
            **user.__dict__,
            "success": True,
        }
    except:
        db.rollback()
    finally:
        db.close()


@router.post("/api/upload")
async def upload(jwt: str = Header(None), file: UploadFile = File(...)):
    try:
        user = db.query(User).filter_by(openid=jwt).first()
        if not user:
            return {'success': False, 'msg': '用户不存在'}
        # 定义保存文件的路径
        out_file_path = f"./static/{file.filename}"
        
        # 使用aiofiles异步写入文件
        async with aiofiles.open(out_file_path, 'wb') as out_file:
            content = await file.read()  # 异步读取内容
            await out_file.write(content)  # 异步写入内容

        user.avatar = file.filename
        db.commit()

        return {"filename": file.filename, "success": True}
    except:
        db.rollback()
    finally:
        db.close()

@router.get("/api/updateUserInfo")
def updateUserInfo(jwt: str = Header(None), type: str = '', value: str = ''):
    try:
        user = db.query(User).filter_by(openid=jwt).first()
        if not user:
            return {'success': False, 'msg': '用户不存在'}
        if type == 'nickname':
            user.nickname = value
            db.commit()

        return {'success': True}
    except:
        db.rollback()
    finally:
        db.close()