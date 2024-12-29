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
        self.group_openid = "238615573D1D80CFC5FECCA7BAF6E266"

    async def on_group_at_message_create(self, message: GroupMessage):
        logger.info(f'on_group_at_message_create: group_openid={message.group_openid}, content={message.content}')
        
        self.group_openid = message.group_openid

        response_content = ""
        if self.message_handler:
            try:
                response_content = await self.message_handler(message.content)
            except Exception as e:
                logger.error(f'Error processing message: {e}')
                response_content = "处理消息时发生错误"

        if response_content == "":
            return

        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0, 
            msg_id=message.id,
            content=response_content)
        
        logger.info(f'on_group_at_message_create result: {messageResult}')

    async def manual_send_message(self, content: str):
        if self.group_openid:
            logger.info(f'主动发消息: group_openid={self.group_openid}, content={content}')

            messageResult = await self.api.post_group_message(
                group_openid=self.group_openid,
                msg_type=0, 
                content=content)
            
            logger.info(f'send_message result: {messageResult}')
        else:
            logger.error('group_openid is not set')

