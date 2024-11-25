import httpx
from typing import Dict, List
from datetime import datetime, timedelta
import pytz

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
    
    def _extract_weibo_text(self, mblog: Dict) -> Dict:
        """提取微博文本信息"""
        return {
            "id": mblog["id"],
            "created_at": mblog["created_at"],
            "text": mblog["text"].replace('<br />', '\n')  # 替换HTML换行为纯文本换行
        }
    
    async def fetch_user_weibo(self, user_id: str) -> Dict:
        """
        获取指定用户的微博内容并处理

        Args:
            user_id: 微博用户ID

        Returns:
            处理后的微博数据
        """
        async with httpx.AsyncClient(headers=self.headers) as client:
            params = {
                "type": "uid",
                "value": user_id,
                "containerid": f"107603{user_id}",
            }
            
            response = await client.get(self.base_url, params=params)
            data = response.json()
            
            if data["ok"] != 1 or "data" not in data:
                return {"error": f"response: {data}"}
            
            # 计算总微博数
            total_weibo = len(data["data"]["cards"])
            print(f"\n总微博数: {total_weibo}")
            
            # 提取所有微博的文本信息
            weibos = []
            for card in data["data"]["cards"]:
                if "mblog" in card:
                    weibo_info = self._extract_weibo_text(card["mblog"])
                    weibos.append(weibo_info)
            
            return {
                "total_count": total_weibo,
                "weibos": weibos
            }