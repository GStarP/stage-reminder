import botpy
from .notification.qq.bot import QQBot
from dotenv import load_dotenv
import os


load_dotenv()

if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True)
    client = QQBot(intents=intents, is_sandbox=True)
    client.run(appid=os.getenv('QQ_BOT_APPID'), secret=os.getenv('QQ_BOT_SECRET'))