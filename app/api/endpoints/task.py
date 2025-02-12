from fastapi import APIRouter, Header
from db.base import db
from models.task import Task
from models.user import User
from datetime import datetime
import time

router = APIRouter()

def updateScore(jwt, score):
    user = db.query(User).filter_by(openid=jwt).first()
    allScore = user.score + score
    user.score = allScore if allScore < 999 else 999
    db.commit()

    return user.score

@router.get("/task")
def task(jwt: str = Header(None), type: str = '', score: int = 0):
    task = db.query(Task).filter_by(openid=jwt).first()
    # 分享朋友圈不重复增加积分
    if type == 'share_circle' and task.share == True:
        score = 0

    task.ad = task.ad == True or type == 'ad'
    task.share = task.share == True or type == 'share'
    task.share_circle = task.share_circle == True or type == 'share_circle'

    db.commit()

    newScore = updateScore(jwt, score)

    return {'success': True, 'score': newScore}

@router.get("/getTaskStatus")
def getTaskStatus(jwt: str = Header(None)):
    task = db.query(Task).filter_by(openid=jwt).first()
    today = datetime.today().strftime("%m-%d")

    if task.sign_date:
        arr = task.sign_date.split(',')
        # 满签则重置
        if len(arr) == 7 and (not (today in arr)):
            task.sign_date = ''
    if task.task_date != today:
        task.ad = False
        task.share = False
        task.share_circle = False
        task.ad = False
        task.task_date = today

    db.commit()
    task = db.query(Task).filter_by(openid=jwt).first()
    
    return {
        **task.__dict__,
        'time': int(round(time.time() * 1000)),
    }

@router.get("/sign")
def task(jwt: str = Header(None), date: str = '', score: int = 0):
    task = db.query(Task).filter_by(openid=jwt).first()

    if not task.sign_date:
        task.sign_date = date
    else:
        task.sign_date += ',' + date
    
    db.commit()

    newScore = updateScore(jwt, score)

    return {'success': True, 'score': newScore}