import botpy
from botpy.message import GroupMessage


class QQBot(botpy.Client):
    async def on_group_at_message_create(self, message: GroupMessage):
        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
              msg_type=0, 
              msg_id=message.id,
              content=f"收到了消息：{message.content}")
        print(messageResult)
        