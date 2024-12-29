import httpx
from typing import Dict
from datetime import datetime
import pytz

from stagereminder.logger import logger

class WeiboCrawler:
    """微博内容抓取器"""
    
    def __init__(self):
        self.base_url = "https://m.weibo.cn/api/container/getIndex"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "application/json, text/plain, */*",
        }
    
    def _parse_weibo_time(self, time_str: str) -> datetime:
        """解析微博时间字符串为datetime对象"""
        return datetime.strptime(time_str, "%a %b %d %H:%M:%S +0800 %Y").replace(tzinfo=pytz.UTC)
    
    def _to_weibo(self, mblog: Dict) -> Dict:
        """提取微博信息"""
        return {
            "id": mblog["id"],
            "created_at": self._parse_weibo_time(mblog["created_at"]),
            "text": mblog["text"],
            "url": f"https://m.weibo.cn/detail/{mblog['id']}"
        }
    
    async def get_recent_weibo_list(self, weibo_user_id: str) -> list[dict]:
        """
        获取指定用户的微博内容并处理

        Args:
            weibo_user_id: 微博用户ID

        Returns:
            处理后的微博数据
        """
        async with httpx.AsyncClient(headers=self.headers) as client:
            params = {
                "type": "uid",
                "value": weibo_user_id,
                "containerid": f"107603{weibo_user_id}",
            }
            
            response = await client.get(self.base_url, params=params)
            data = response.json()
            
            if data["ok"] != 1 or "data" not in data:
                raise Exception(f'{data}')
            
            # 计算总微博数
            total_count = len(data["data"]["cards"])
            logger.info(f"总微博数: {total_count}")
            
            # 提取所有微博信息
            weibos = []
            for card in data["data"]["cards"]:
                if "mblog" in card:
                    weibo = self._to_weibo(card["mblog"])
                    weibos.append(weibo)
            
            return weibos