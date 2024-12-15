import logging
from datetime import datetime
from typing import List, Optional
from .db_manager import DBManager
from stagereminder.crawler.weibo import WeiboCrawler
from stagereminder.extractor.llm import LLMExtractor
from stagereminder.logger import logger

class StageReminderService:
    def __init__(self, llm_api_key: str):
        self.db = DBManager()
        self.crawler = WeiboCrawler()
        self.extractor = LLMExtractor(api_key=llm_api_key)

    async def handle_query_message(self, content: str) -> str:
        """处理用户查询请求，返回格式化的演出信息"""
        try:
            artists = self.db.get_all_artists()
            if not artists:
                return "当前没有关注任何艺人哦～"

            message = "\n━━━━━━━━━━━━━━"
            has_stages = False
            
            for artist in artists:
                stages = self.db.get_artist_stages(artist.id)
                if stages:  # 只有当艺人有演出信息时才添加到消息中
                    message += self._format_artist_stages(artist, stages)
                    has_stages = True

            return message if has_stages else "当前没有即将进行的演出哦～"

        except Exception as e:
            logger.error(f"Error handling query message: {e}")
            return "抱歉，查询演出信息时出现错误。"

    async def update_stages(self):
        """更新所有艺人的演出信息"""
        try:
            artists = self.db.get_all_artists()
            for artist in artists:
                logger.info(f"Updating stages for artist: {artist.name}")
                
                # 获取微博内容
                weibos = await self.crawler.fetch_user_weibo(artist.weibo_uid)
                if isinstance(weibos, dict) and "error" in weibos:
                    logger.error(f"Failed to fetch weibo for {artist.name}: {weibos['error']}")
                    continue

                # 处理每条微博
                for weibo in weibos:
                    # 尝试提取演出信息
                    result = await self.extractor.extract_stage_info(weibo['text'])
                    
                    if result['found']:
                        stage_info = result['stage_info']
                        # 转换为数据库需要的格式
                        stage_data = {
                            'name': stage_info['stage_name'],
                            'show_time': self._parse_datetime(stage_info['stage_time']),
                            'details': {
                                'venue': stage_info['stage_location'],
                                'ticket_time': self._parse_datetime(stage_info['ticket_time']),
                                'price': stage_info.get('ticket_price'),
                                'platform': stage_info.get('ticket_platform'),
                                'artists': stage_info.get('artists'),
                                'organizer': stage_info.get('organizer'),
                                'description': stage_info.get('description')
                            },
                            'weibo_url': weibo['url']
                        }
                        # 保存到数据库
                        self.db.add_or_update_stage(artist.id, stage_data)

        except Exception as e:
            logger.error(f"Error updating stages: {e}")
            raise

    def _format_artist_stages(self, artist, stages) -> str:
        """格式化单个艺人的演出信息"""
        message = f"\n👤 {artist.name}\n"
        for stage in stages:
            message += f"\n"
            message += f"📅 {stage.name}\n"
            message += f"⏰ {stage.show_time.strftime('%Y-%m-%d %H:%M') if stage.show_time.time().strftime('%H:%M') != '00:00' else stage.show_time.strftime('%Y-%m-%d')}\n"
            
            if stage.details:
                if stage.details.get('venue'):
                    message += f"📍 {stage.details['venue']}\n"
                if stage.details.get('price'):
                    message += f"💰 {stage.details['price']}\n"
                if stage.details.get('ticket_time'):
                    message += f"🎫 开票时间：{stage.details['ticket_time']}\n"
                if stage.details.get('platform'):
                    message += f"🎪 售票平台：{stage.details['platform']}\n"
            
            # TODO: QQ机器人不允许发送URL
            # if stage.weibo_url:
            #     message += f"🔗 详情：{stage.weibo_url}\n"

        message += f'━━━━━━━━━━━━━━'

        return message
    
    def _parse_datetime(self, time_str: str) -> datetime:
        """
        解析不同格式的时间字符串，并确保日期不早于当年
        
        Args:
            time_str: 时间字符串，可能的格式包括：
                    - YYYY-MM-DD HH:mm
                    - YYYY-MM-DD HH
                    - YYYY-MM-DD
        
        Returns:
            datetime 对象，如果只有日期，时间默认为 00:00
            如果年份早于当年，则将年份设置为当年
        """
        formats = [
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H',
            '%Y-%m-%d',
            '%Y-%m',
        ]
        
        current_year = datetime.now().year
        parsed_time = None
        
        for fmt in formats:
            try:
                parsed_time = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_time is None:
            raise ValueError(f"无法解析的时间格式: {time_str}")
        
        # 如果年份早于当年，将年份设置为当年
        if parsed_time.year < current_year:
            parsed_time = parsed_time.replace(year=current_year)
        
        return parsed_time
    
