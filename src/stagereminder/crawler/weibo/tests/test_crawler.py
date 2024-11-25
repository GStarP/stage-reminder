import pytest
from stagereminder.crawler.weibo.crawler import WeiboCrawler

@pytest.mark.asyncio
async def test_fetch_user_weibo():
    """测试获取用户微博内容"""
    # 初始化爬虫
    crawler = WeiboCrawler()
    
    # 使用银临的微博ID作为测试
    user_id = "2266537042"
    
    # 调用接口获取数据
    result = await crawler.fetch_user_weibo(user_id)
    
    # 基本数据格式验证
    assert isinstance(result, dict)
    
    # 打印返回数据，方便调试
    print(result)