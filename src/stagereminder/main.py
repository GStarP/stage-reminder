import botpy
from stagereminder.notification.qq.bot import QQBot
from stagereminder.manager.service import StageReminderService
from dotenv import load_dotenv
import os


load_dotenv()

if __name__ == "__main__":

    service = StageReminderService(llm_api_key=os.getenv('DEEPSEEK_API_KEY'))

    intents = botpy.Intents(public_messages=True)
    client = QQBot(message_handler=service.handle_query_message, intents=intents, is_sandbox=True)
    client.run(appid=os.getenv('QQ_BOT_APPID'), secret=os.getenv('QQ_BOT_SECRET'))