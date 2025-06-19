from fastapi import APIRouter, Header
from db.base import db
from models.task import Task
from models.user import User
from datetime import datetime, timedelta
import time

router = APIRouter()

def updateScore(jwt, score):
    try:
        user = db.query(User).filter_by(openid=jwt).first()
        allScore = user.score + score
        user.score = allScore if allScore < 999 else 999
        db.commit()
        return user.score
    except:
        db.rollback()
    finally:
        db.close()

@router.get("/api/task")
def task(jwt: str = Header(None), taskType: str = '', score: int = 0):
    try:
        task = db.query(Task).filter_by(openid=jwt).first()
        if not task:
            return {'success': False, 'msg': '用户不存在'}
        try:
            int(score)
            # 分享朋友圈不重复增加积分
            if taskType == 'share_circle' and task.share_circle == True:
                score = 0
        except:
            score = 0
        finally:
            task.ad = task.ad == True or taskType == 'ad'
            task.ad2 = task.ad2 == True or taskType == 'ad2'
            task.ad3 = task.ad3 == True or taskType == 'ad3'
            task.share = task.share == True or taskType == 'share'
            task.share_circle = task.share_circle == True or taskType == 'share_circle'
            task.share_count = taskType == 'share_count' or 3 if task.share_count == 3 else task.share_count + 1
            newScore = updateScore(jwt, score)
            return {'success': True, 'score': newScore}
    except:
        db.rollback()
    finally:
        db.close()

@router.get("/api/getTaskStatus")
def getTaskStatus(jwt: str = Header(None)):
    try:
        task = db.query(Task).filter_by(openid=jwt).first()
        if not task:
            return {'success': False, 'msg': '用户不存在'}
        today = datetime.today().strftime("%m-%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%m-%d")
        if task.sign_date:
            arr = task.sign_date.split(',')
            # 满签则重置
            if len(arr) == 7 and (not (today in arr)):
                task.sign_date = ''
            # 断签则重置
            if today not in arr and yesterday not in arr:
                task.sign_date = ''
        if task.task_date != today:
            task.ad = False
            task.ad2 = False
            task.ad3 = False
            task.share = False
            task.share_circle = False
            task.task_date = today
            task.share_count = 0
        db.commit()
    except:
            db.rollback()
    finally:
        db.close()
    
    task = db.query(Task).filter_by(openid=jwt).first()

    return {
        **task.__dict__,
        'time': int(round(time.time() * 1000)),
        'success': True
    }

@router.get("/api/sign")
def task(jwt: str = Header(None), date: str = '', score: int = 0):
    try:
        task = db.query(Task).filter_by(openid=jwt).first()
        if not task:
            return {'success': False, 'msg': '用户不存在'}
        if not task.sign_date:
            task.sign_date = date
        else:
            task.sign_date += ',' + date
        
        newScore = updateScore(jwt, score)

        return {'success': True, 'score': newScore}
    except:
        db.rollback()
    finally:
        db.close()