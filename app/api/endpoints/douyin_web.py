from fastapi import APIRouter, Query, Request, HTTPException  # 导入FastAPI组件
from app.api.models.APIResponseModel import ResponseModel, ErrorResponseModel  # 导入响应模型

from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫


router = APIRouter()
DouyinWebCrawler = DouyinWebCrawler()


# 获取单个作品数据
@router.get("/fetch_one_video", response_model=ResponseModel, summary="获取单个作品数据/Get single video data")
async def fetch_one_video(request: Request,
                          aweme_id: str = Query(example="7372484719365098803", description="作品id/Video id")):
    """
    # [中文]
    ### 用途:
    - 获取单个作品数据
    ### 参数:
    - aweme_id: 作品id
    ### 返回:
    - 作品数据
    """
    try:
        data = await DouyinWebCrawler.fetch_one_video(aweme_id)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())

# 提取单个作品id
@router.get("/get_aweme_id",
            response_model=ResponseModel,
            summary="提取单个作品id/Extract single video id")
async def get_aweme_id(request: Request,
                       url: str = Query(example="https://www.douyin.com/video/7298145681699622182")):
    """
    # [中文]
    ### 用途:
    - 提取单个作品id
    ### 参数:
    - url: 作品链接
    ### 返回:
    - 作品id
    """
    try:
        data = await DouyinWebCrawler.get_aweme_id(url)
        return ResponseModel(code=200,
                             router=request.url.path,
                             data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code,
                                    router=request.url.path,
                                    params=dict(request.query_params),
                                    )
        raise HTTPException(status_code=status_code, detail=detail.dict())