import pytest
import json
from datetime import datetime
from stagereminder.crawler.weibo import WeiboCrawler
from stagereminder.logger import logger

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')  # 使用指定格式
        return super().default(obj)

@pytest.mark.asyncio
async def test_fetch_user_weibo():
    """测试获取用户微博内容"""
    # 初始化爬虫
    crawler = WeiboCrawler()
    
    # 使用银临的微博ID作为测试
    user_id = "2266537042"
    
    # 调用接口获取数据
    weibos = await crawler.fetch_user_weibo(user_id)
    
    # 基本数据格式验证
    assert isinstance(weibos, list)
    
    # 打印返回数据，方便调试
    logger.info(json.dumps(weibos, ensure_ascii=False, cls=DateTimeEncoder))