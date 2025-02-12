import asyncio
import httpx
from fastapi import APIRouter, Header
from crawlers.hybrid.hybrid_crawler import HybridCrawler
from db.base import db
from models.user import User

HybridCrawler = HybridCrawler()

router = APIRouter()

@router.get("/dyVideo/")
def read_root(jwt: str = Header(None), url: str = ''):
    res = asyncio.run(HybridCrawler.hybrid_parsing_single_video(url))
    if res:
        user = db.query(User).filter_by(openid=jwt).first()
        user.score -= 2
        db.commit()
    return res

@router.get("/redirect")
async def get_redirect_url(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=False)
        if response.status_code in (301, 302):
            redirect_url = response.headers.get('Location')
            return {"redirect_url": redirect_url}
        else:
            return {"redirect_url": url}