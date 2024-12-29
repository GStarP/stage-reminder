from stagereminder.logger import logger
import botpy
from stagereminder.notification.qq_bot import QQBot
from dotenv import load_dotenv
import os
from stagereminder.main.db_manager import DBManager



# 加载环境变量
load_dotenv()

# 初始化服务
db = DBManager()


def _generate_notify_content(query: str = None) -> str:
    """处理用户查询请求，返回格式化的演出信息"""
    try:
        artists = db.get_all_artists()
        if not artists:
            return "当前没有关注任何艺人哦～"

        message = "\n━━━━━━━━━━━━━━"
        has_stages = False
        
        # 查找是否有匹配的艺人名称
        if query:
            matched_artists = [artist for artist in artists if query.lower().strip() in artist.name.lower().strip()]
            logger.info(f"符合查询条件的艺人: {matched_artists}")
        else:
            matched_artists = artists
        
        # 如果找到匹配的艺人，只显示匹配艺人的演出
        # 如果没有找到匹配的艺人，显示所有艺人的演出
        target_artists = matched_artists if len(matched_artists) > 0 else artists
        
        for artist in target_artists:
            stages = db.get_artist_stages(artist.id)
            if stages:  # 只有当艺人有演出信息时才添加到消息中
                message += _format_artist_stages(artist, stages)
                has_stages = True

        return message if has_stages else "当前没有即将进行的演出哦～"

    except Exception as e:
        logger.error(f"Error handling query message: {e}")
        return "抱歉，查询演出信息时出现错误。"

def _format_artist_stages(artist, stages) -> str:
    """格式化单个艺人的演出信息"""
    message = f"\n👤 {artist.name}\n"
    for stage in stages:
        message += f"\n"
        message += f"📅 {stage.stage_name}\n"
        stage_time_str = _format_datetime(stage.detail.get('stage_time')) if stage.detail.get('stage_time') else stage.stage_time.strftime('%Y-%m-%d %H:%M')
        message += f"⏰ {stage_time_str}\n"
        
        if stage.detail:
            if stage.detail.get('stage_location'):
                message += f"📍 {stage.detail['stage_location']}\n"
            if stage.detail.get('ticket_price'):
                message += f"💰 {stage.detail['ticket_price']}\n"
            if stage.detail.get('ticket_time'):
                message += f"🎫 开票时间：{stage.detail['ticket_time']}\n"
            if stage.detail.get('platform'):
                message += f"🎪 售票平台：{stage.detail['platform']}\n"
        
        # TODO: QQ机器人不允许发送URL
        # if stage.weibo_url:
        #     message += f"🔗 详情：{stage.weibo_url}\n"

    message += f'━━━━━━━━━━━━━━'

    return message

def _format_datetime(time_dict: dict) -> str:
    res = ""

    year = time_dict.get('year')
    month = time_dict.get('month')
    day = time_dict.get('day')
    hour = time_dict.get('hour')
    minute = time_dict.get('minute')

    if year:
        res += f'{year}年'
    if month:
        res += f'{month}月'
    if day:
        res += f'{day}日'
    if hour:
        res += f'{hour}时'
    if minute:
        res += f'{minute}分'

    return res

def notify_stage():
    intents = botpy.Intents(public_messages=True)
    bot = QQBot(intents=intents, is_sandbox=True)
    bot.on_ready = lambda: bot.manual_send_message(_generate_notify_content())
    bot.run(appid=os.getenv('QQ_BOT_APPID'), secret=os.getenv('QQ_BOT_SECRET'))
    

if __name__ == "__main__":
    notify_stage()
