import requests
from fastapi import APIRouter, Header, UploadFile, File
from db.base import db
from models.user import User
from models.task import Task
import aiofiles

router = APIRouter()

@router.get("/login")
def login(code):
    response = requests.get("https://api.weixin.qq.com/sns/jscode2session?appid=wx5bb2b38dcb169957&secret=4bcbe7130c538dda3864b49bf9f1b8c9&grant_type=authorization_code&js_code=" + code)
    res = response.json()
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
    )
        db.add(newUser)
        db.add(newTask)
        db.commit()

    return res

@router.get("/findUserInfo")
def findUserInfo(jwt: str = Header(None)):
    user = db.query(User).filter_by(openid=jwt).first()

    return user

@router.post("/upload")
async def upload(jwt: str = Header(None), file: UploadFile = File(...)):
    # 定义保存文件的路径
    out_file_path = f"./static/{file.filename}"
    
    # 使用aiofiles异步写入文件
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # 异步读取内容
        await out_file.write(content)  # 异步写入内容

    user = db.query(User).filter_by(openid=jwt).first()
    user.avatar = file.filename
    db.commit()

    return {"filename": file.filename}

@router.get("/updateUserInfo")
def updateUserInfo(jwt: str = Header(None), type: str = '', value: str = ''):
    user = db.query(User).filter_by(openid=jwt).first()

    if type == 'nickname':
        user.nickname = value

    db.commit()

    return {'success': True}