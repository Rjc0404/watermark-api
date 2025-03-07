import asyncio
import httpx
from fastapi import APIRouter, Header
import requests
import bs4
from crawlers.hybrid.hybrid_crawler import HybridCrawler
from db.base import db
from models.user import User

HybridCrawler = HybridCrawler()

router = APIRouter()

# @router.middleware("http")
# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception as e:
#         logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
#         return JSONResponse(
#             status_code=500,
#             content={"detail": "Internal server error occurred. Please try again later."}
#         )

def updateScore(jwt):
    user = db.query(User).filter_by(openid=jwt).first()
    user.score -= 2
    db.commit()

@router.get("/api/dyVideo/")
def read_root(jwt: str = Header(None), url: str = ''):
    res = asyncio.run(HybridCrawler.hybrid_parsing_single_video(url))
    if res:
        try:
            updateScore(jwt)
        except:
            return {'success': False, 'msg': '用户不存在'}
    return {
        **res,
        "success": True
    }

@router.get("/api/redirect")
async def get_redirect_url(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=False)
        if response.status_code in (301, 302):
            redirect_url = response.headers.get('Location')
            return {"success": True, "redirect_url": redirect_url}
        else:
            return {"success": True, "redirect_url": url}
        
@router.get("/api/xhsParse")
def xhsParse(jwt: str = Header(None), url: str = ''):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    }
    try:
        content = requests.get(url, headers=headers, ).text
    except Exception as e:
        print(f"Error occurred: {e}")
        return (f"Error occurred: {e}")
    html_content = content
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    # 初始化一个字典来存储我们要返回的数据
    data = {}
    # 提取所有图片链接
    images = [meta['content'] for meta in soup.find_all('meta', attrs={'name': 'og:image'})]

    # 提取视频链接
    video_tags = soup.find_all('meta', attrs={'name': 'og:video'})

    # # 提取文本关键字和描述
    # keywords = soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find('meta', attrs={
    #     'name': 'keywords'}) else None
    # description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={
    #     'name': 'description'}) else None
    # # 提取标题
    # title = soup.find('meta', attrs={'name': 'og:title'})['content'] if soup.find('meta', attrs={
    #     'name': 'og:title'}) else None
    # title = title.replace(" - 小红书", "")
    # # 提取特定社交媒体平台的元数据（这里假设它们存在）
    # comment = soup.find('meta', attrs={'name': 'og:xhs:note_comment'})['content'] if soup.find('meta', attrs={
    #     'name': 'og:xhs:note_comment'}) else None
    # like = soup.find('meta', attrs={'name': 'og:xhs:note_like'})['content'] if soup.find('meta', attrs={
    #     'name': 'og:xhs:note_like'}) else None
    # collect = soup.find('meta', attrs={'name': 'og:xhs:note_collect'})['content'] if soup.find('meta', attrs={
    #     'name': 'og:xhs:note_collect'}) else None
    # videotime = soup.find('meta', attrs={'name': 'og:videotime'})['content'] if soup.find('meta', attrs={
    #     'name': 'og:videotime'}) else None
    # data['title'] = title
    # data['description'] = description
    # data['keywords'] = keywords
    # data['like'] = like
    # data['collect'] = collect
    # data['comment'] = comment
    # data['videotime'] = videotime

    newImages = [imgUrl if 'https' in imgUrl else imgUrl.replace('http', 'https') for imgUrl in images]

    data['images'] = newImages
    data['videos'] = [tag['content'] for tag in video_tags] if video_tags else ''
    # 提取rel属性为"preload"的link标签
    # cover_img = [link.get('href') for link in soup.find_all('link', rel="preload") if link.get('href')]
    # if cover_img:
    #     data['cover_img'] = cover_img
        # 返回JSON格式的字典

    if data['images'] or data['videos']:
        try:
            updateScore(jwt)
        except:
            return {'success': False, 'msg': '用户不存在'}
        else:
            return {
                **data,
                "success": True
            }
    else:
        return {
            "success": False,
            "msg": "No images or videos found."
        }
   