import os
import asyncio
from stagereminder.logger import logger
from dotenv import load_dotenv
from stagereminder.main.db_manager import DBManager
from stagereminder.crawler.weibo import WeiboCrawler
from stagereminder.parser.stage_parser import StageParser


# 加载环境变量
load_dotenv()

# 初始化服务
db = DBManager()
crawler = WeiboCrawler()
parser = StageParser(api_key=os.getenv("DEEPSEEK_API_KEY"))


async def update_stages():
    """更新所有艺人的演出信息"""
    try:
        artists = db.get_all_artists()
        for artist in artists:
            logger.info(f"开始收集演出信息: {artist.name}")
            
            # 获取微博内容
            weibos = await crawler.get_recent_weibo_list(artist.weibo_uid)
            if isinstance(weibos, dict) and "error" in weibos:
                logger.error(f"Failed to fetch weibo for {artist.name}: {weibos['error']}")
                continue

            # 处理每条微博
            for weibo in weibos:
                # 尝试提取演出信息
                result = await parser.parse_weibo(weibo)
                
                if result['found']:
                    # 转换为数据库需要的格式
                    stage = result['stage']
                    detail = {}
                    if stage.get('stage_time'):
                        detail['stage_time'] = stage['stage_time']
                    if stage.get('stage_location'):
                        detail['stage_location'] = stage['stage_location']
                    if stage.get('ticket_time'):
                        detail['ticket_time'] = stage['ticket_time']
                    if stage.get('ticket_timestamp'):
                        detail['ticket_timestamp'] = stage['ticket_timestamp']
                    if stage.get('ticket_price'):
                        detail['ticket_price'] = stage['ticket_price']
                    if stage.get('ticket_platform'):
                        detail['ticket_platform'] = stage['ticket_platform']

                    stage_data = {
                        'stage_name': stage['stage_name'],
                        'stage_time': stage['stage_timestamp'],
                        'detail': detail,
                        'weibo_id': weibo['id']
                    }
                    # 保存到数据库
                    db.add_or_update_stage(artist.id, stage_data)

    except Exception as e:
        logger.error(f"收集演出信息时发生错误: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(update_stages())