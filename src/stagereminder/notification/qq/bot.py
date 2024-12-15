import botpy
from botpy.message import GroupMessage
from typing import Callable, Awaitable
from stagereminder.logger import logger

class QQBot(botpy.Client):
    def __init__(self, message_handler: Callable[[str], Awaitable[str]] = None, **options):
        """
        初始化 QQ 机器人
        
        Args:
            message_handler: 异步回调函数，接收消息内容字符串，返回响应内容字符串
            **options: 传递给父类的其他参数
        """
        super().__init__(**options)
        self.message_handler = message_handler

    async def on_group_at_message_create(self, message: GroupMessage):
        logger.info(f'on_group_at_message_create: group_openid={message.group_openid}, content={message.content}')

        response_content = "收到了消息"
        if self.message_handler:
            try:
                response_content = await self.message_handler(message.content)
            except Exception as e:
                logger.error(f'Error processing message: {e}')
                response_content = "处理消息时发生错误"

        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0, 
            msg_id=message.id,
            content=response_content)
        
        logger.info(f'messageResult: {messageResult}')
        