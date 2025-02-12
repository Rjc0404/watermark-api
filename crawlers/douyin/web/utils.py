import json
import os
import random
import re
import time
from urllib.parse import quote

# import execjs
import httpx
import yaml

from crawlers.douyin.web.xbogus import XBogus as XB
from crawlers.douyin.web.abogus import ABogus as AB

from crawlers.utils.api_exceptions import (
    APIConnectionError,
    APIResponseError,
)
from crawlers.utils.utils import (
    gen_random_str,
    get_timestamp,
)

# 配置文件路径
# Read the configuration file
path = os.path.abspath(os.path.dirname(__file__))

# 读取配置文件
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class TokenManager:
    douyin_manager = config.get("TokenManager").get("douyin")
    token_conf = douyin_manager.get("msToken", None)
    ttwid_conf = douyin_manager.get("ttwid", None)
    proxies_conf = douyin_manager.get("proxies", None)
    proxies = {
        # "http://": proxies_conf.get("http", None),
        "https://": proxies_conf.get("https", None),
    }

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的msToken,当出现错误时返回虚假的值
        (Generate a real msToken and return a false value when an error occurs)
        """

        payload = json.dumps(
            {
                "magic": cls.token_conf["magic"],
                "version": cls.token_conf["version"],
                "dataType": cls.token_conf["dataType"],
                "strData": cls.token_conf["strData"],
                "tspFromClient": get_timestamp(),
            }
        )
        headers = {
            "User-Agent": cls.token_conf["User-Agent"],
            "Content-Type": "application/json",
        }

        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport, proxies=cls.proxies) as client:
            try:
                response = client.post(
                    cls.token_conf["url"], content=payload, headers=headers
                )
                response.raise_for_status()

                msToken = str(httpx.Cookies(response.cookies).get("msToken"))
                if len(msToken) not in [120, 128]:
                    raise APIResponseError("响应内容：{0}， Douyin msToken API 的响应内容不符合要求。".format(msToken))

                return msToken

            except Exception as e:
                # 返回虚假的msToken (Return a fake msToken)
                return cls.gen_false_msToken()

    @classmethod
    def gen_false_msToken(cls) -> str:
        """生成随机msToken (Generate random msToken)"""
        return gen_random_str(126) + "=="

class VerifyFpManager:
    @classmethod
    def gen_verify_fp(cls) -> str:
        """
        生成verifyFp 与 s_v_web_id (Generate verifyFp)
        """
        base_str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        t = len(base_str)
        milliseconds = int(round(time.time() * 1000))
        base36 = ""
        while milliseconds > 0:
            remainder = milliseconds % 36
            if remainder < 10:
                base36 = str(remainder) + base36
            else:
                base36 = chr(ord("a") + remainder - 10) + base36
            milliseconds = int(milliseconds / 36)
        r = base36
        o = [""] * 36
        o[8] = o[13] = o[18] = o[23] = "_"
        o[14] = "4"

        for i in range(36):
            if not o[i]:
                n = 0 or int(random.random() * t)
                if i == 19:
                    n = 3 & n | 8
                o[i] = base_str[n]

        return "verify_" + r + "_" + "".join(o)

    @classmethod
    def gen_s_v_web_id(cls) -> str:
        return cls.gen_verify_fp()


class BogusManager:

    # 字符串方法生成X-Bogus参数
    @classmethod
    def xb_str_2_endpoint(cls, endpoint: str, user_agent: str) -> str:
        try:
            final_endpoint = XB(user_agent).getXBogus(endpoint)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        return final_endpoint[0]

    # 字典方法生成X-Bogus参数
    @classmethod
    def xb_model_2_endpoint(cls, base_endpoint: str, params: dict, user_agent: str) -> str:
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XB(user_agent).getXBogus(param_str)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint

    # 字符串方法生成A-Bogus参数
    # TODO: 未完成测试，暂时不提交至主分支。
    # @classmethod
    # def ab_str_2_endpoint_js_ver(cls, endpoint: str, user_agent: str) -> str:
    #     try:
    #         # 获取请求参数
    #         endpoint_query_params = urllib.parse.urlparse(endpoint).query
    #         # 确定A-Bogus JS文件路径
    #         js_path = os.path.dirname(os.path.abspath(__file__))
    #         a_bogus_js_path = os.path.join(js_path, 'a_bogus.js')
    #         with open(a_bogus_js_path, 'r', encoding='utf-8') as file:
    #             js_code = file.read()
    #         # 此处需要使用Node环境
    #         # - 安装Node.js
    #         # - 安装execjs库
    #         # - 安装NPM依赖
    #         # - npm install jsdom
    #         node_runtime = execjs.get('Node')
    #         context = node_runtime.compile(js_code)
    #         arg = [0, 1, 0, endpoint_query_params, "", user_agent]
    #         a_bougus = quote(context.call('get_a_bogus', arg), safe='')
    #         return a_bougus
    #     except Exception as e:
    #         raise RuntimeError("生成A-Bogus失败: {0})".format(e))

    # 字典方法生成A-Bogus参数，感谢 @JoeanAmier 提供的纯Python版本算法。
    @classmethod
    def ab_model_2_endpoint(cls, params: dict, user_agent: str) -> str:
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        try:
            ab_value = AB().get_value(params, )
        except Exception as e:
            raise RuntimeError("生成A-Bogus失败: {0})".format(e))

        return quote(ab_value, safe='')

class AwemeIdFetcher:
    # 预编译正则表达式
    _DOUYIN_VIDEO_URL_PATTERN = re.compile(r"video/([^/?]*)")
    _DOUYIN_NOTE_URL_PATTERN = re.compile(r"note/([^/?]*)")
    _DOUYIN_DISCOVER_URL_PATTERN = re.compile(r"modal_id=([0-9]+)")

    @classmethod
    async def get_aweme_id(cls, url: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                video_pattern = cls._DOUYIN_VIDEO_URL_PATTERN
                note_pattern = cls._DOUYIN_NOTE_URL_PATTERN
                discover_pattern = cls._DOUYIN_DISCOVER_URL_PATTERN
                
                match = video_pattern.search(str(response.url))
                if match:
                    aweme_id = match.group(1)
                else:
                    match = note_pattern.search(str(response.url))
                    if match:
                        aweme_id = match.group(1)
                    else:
                        match = discover_pattern.search(str(response.url))
                        if match:
                            aweme_id = match.group(1)
                        else:
                            raise APIResponseError(
                                "未在响应的地址中找到aweme_id，检查链接是否为作品页"
                            )
                return aweme_id

            except httpx.RequestError as exc:
                # 捕获所有与 httpx 请求相关的异常情况 (Captures all httpx request-related exceptions)
                raise APIConnectionError("请求端点失败，请检查当前网络环境。 链接：{0}，代理：{1}，异常类名：{2}，异常详细信息：{3}"
                                         .format(url, TokenManager.proxies, cls.__name__, exc)
                                         )

            except httpx.HTTPStatusError as e:
                raise APIResponseError("链接：{0}，状态码 {1}：{2} ".format(
                    e.response.url, e.response.status_code, e.response.text
                )
                )

class MixIdFetcher:
    # 获取方法同AwemeIdFetcher
    @classmethod
    async def get_mix_id(cls, url: str) -> str:
        return


class WebCastIdFetcher:
    # 预编译正则表达式
    _DOUYIN_LIVE_URL_PATTERN = re.compile(r"live/([^/?]*)")
    # https://live.douyin.com/766545142636?cover_type=0&enter_from_merge=web_live&enter_method=web_card&game_name=&is_recommend=1&live_type=game&more_detail=&request_id=20231110224012D47CD00C18B4AE4BFF9B&room_id=7299828646049827596&stream_type=vertical&title_type=1&web_live_page=hot_live&web_live_tab=all
    # https://live.douyin.com/766545142636
    _DOUYIN_LIVE_URL_PATTERN2 = re.compile(r"http[s]?://live.douyin.com/(\d+)")
    # https://webcast.amemv.com/douyin/webcast/reflow/7318296342189919011?u_code=l1j9bkbd&did=MS4wLjABAAAAEs86TBQPNwAo-RGrcxWyCdwKhI66AK3Pqf3ieo6HaxI&iid=MS4wLjABAAAA0ptpM-zzoliLEeyvWOCUt-_dQza4uSjlIvbtIazXnCY&with_sec_did=1&use_link_command=1&ecom_share_track_params=&extra_params={"from_request_id":"20231230162057EC005772A8EAA0199906","im_channel_invite_id":"0"}&user_id=3644207898042206&liveId=7318296342189919011&from=share&style=share&enter_method=click_share&roomId=7318296342189919011&activity_info={}
    _DOUYIN_LIVE_URL_PATTERN3 = re.compile(r"reflow/([^/?]*)")