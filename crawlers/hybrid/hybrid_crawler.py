from crawlers.douyin.web.web_crawler import DouyinWebCrawler  # 导入抖音Web爬虫

class HybridCrawler:
    def __init__(self):
        self.DouyinWebCrawler = DouyinWebCrawler()

    async def hybrid_parsing_single_video(self, url: str):
        if "douyin" in url:
            platform = "douyin"
            aweme_id = await self.DouyinWebCrawler.get_aweme_id(url)
            if not aweme_id:
                return {'success': False, 'msg': '获取视频ID失败'}
            data = await self.DouyinWebCrawler.fetch_one_video(aweme_id)
            if not data:
                return {'success': False, 'msg': '获取视频数据失败'}
            data = data.get("aweme_detail")
            aweme_type = data.get("aweme_type")

        url_type_code_dict = {
            # common
            0: 'video',
            # Douyin
            2: 'image',
            4: 'video',
            68: 'image',
        }
        url_type = url_type_code_dict.get(aweme_type, 'video')

        result_data = {
            'type': url_type,
            # 'platform': platform,
            # 'aweme_id': aweme_id,
            # 'desc': data.get("desc"),
            # 'create_time': data.get("create_time"),
            # 'author': data.get("author"),
            # 'music': data.get("music"),
            # 'statistics': data.get("statistics"),
            # 'cover_data': {
            #     'cover': data.get("video").get("cover"),
            #     'origin_cover': data.get("video").get("origin_cover"),
            #     'dynamic_cover': data.get("video").get("dynamic_cover")
            # },
            # 'hashtags': data.get('text_extra'),
        }
        # 创建一个空变量，稍后使用.update()方法更新数据the data
        api_data = None
        # 判断链接类型并处理数据/Judge link type and process data
        # 抖音数据处理/Douyin data processing
        if platform == 'douyin':
            # 抖音视频数据处理/Douyin video data processing
            if url_type == 'video':
                # 将信息储存在字典中/Store information in a dictionary
                uri = data['video']['play_addr']['uri']
                api_data = {
                    'video_data': f"https://aweme.snssdk.com/aweme/v1/play/?video_id={uri}&line=0"
                }
            # 抖音图片数据处理/Douyin image data processing
            elif url_type == 'image':
                # 无水印图片列表/No watermark image list
                no_watermark_image_list = []
                # 有水印图片列表/With watermark image list
                # watermark_image_list = []
                # 遍历图片列表/Traverse image list
                for i in data['images']:
                    no_watermark_image_list.append(i['url_list'][0])
                    # watermark_image_list.append(i['download_url_list'][0])
                api_data = {
                    'image_data': no_watermark_image_list,
                }
        # 更新数据/Update data
        result_data.update(api_data)
        return result_data
