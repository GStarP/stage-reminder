from openai import AsyncOpenAI
from typing import Dict, Optional
from datetime import datetime
import json
from stagereminder.logger import logger

class StageParser:
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(base_url="https://api.deepseek.com/v1", api_key=api_key)
        self.system_prompt = """
## 角色
你是一个能够准确分析微博内容的助手。你的任务是判断微博内容是否包含演出预告信息，如果包含，则从微博内容中提取演出预告信息。

## 任务
- 第一步：判断微博内容是否包含演出预告信息，如果不包含直接返回 `{"found": false}`，如果包含则进行第二步。
- 第二步：从微博内容中提取演出预告信息，并返回 `{"found": true, "stage": {...}}`。
  - 演出预告信息的字段如下：
    - stage_name: 演出名称 (str)(required)
    - stage_time: 演出时间 (datetime)(required)
    - stage_location: 演出地点 (str)(required)
    - ticket_time: 售票时间 (datetime)
    - ticket_price: 票价信息 (str)
    - ticket_platform: 售票平台 (str)

请以 JSON 格式输出！

## 注意事项
- 即使微博内容包含演出相关信息，也未必是演出预告信息，还有可能是演出结束后的回顾，请仔细甄别。我的建议是，当微博内容包含演出时间和演出地点，且具有明显的"预告"性质时，才认为其包含演出预告信息。
- datetime 类型的提取要求：
  - 一定是单个时间，而非时间范围，如果有识别出一个时间范围，请提取其开始时间。
  - 只关注年、月、日、时、分，并以 dict 的形式返回。
    - 示例格式：`{"year": 2024, "month": 12, "day": 28, "hour": 10, "minute": 30}`
  - 如果只提取到部分信息，应该只返回提取到的部分，不要自己填充。例如只提取到月和日的信息，应该返回 `{"month": 12, "day": 28}`
- 演出地点不一定是一个物理地点，你应该先判断演出是否为线上演出，如果是线上演出，则演出地点更可能是线上平台。
"""

    def __infer_stage_time(self, time_info_dict: dict) -> datetime:
        """
        根据不一定全的时间信息推断时间
        """
        year = time_info_dict.get('year') or datetime.now().year
        month = time_info_dict.get('month') or datetime.now().month
        day = time_info_dict.get('day') or 1
        hour = time_info_dict.get('hour') or 0
        minute = time_info_dict.get('minute') or 0
       
        return datetime(year, month, day, hour, minute)

    async def parse_weibo(self, weibo: dict) -> Optional[Dict]:
        """
        从微博内容中提取演出相关信息

        Args:
            weibo: 微博信息

        Returns:
            提取的演出预告信息或空结果
        """
        weibo_text = weibo['text']
        weibo_time = weibo['created_at']

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请分析以下微博：\n\n微博内容：{weibo_text}\n\n微博发布时间：{weibo_time}"}
        ]
        
        logger.info(f'正在分析推文：[{weibo_time}] {weibo_text}')
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0,
            response_format={ "type": "json_object" }
        )

        result = json.loads(response.choices[0].message.content)
        logger.info(f'分析完成：{result}')

        if result['found']:
            stage = result['stage']
            if stage.get('stage_time'):
                stage['stage_timestamp'] = self.__infer_stage_time(stage['stage_time'])
                logger.info(f'推断演出时间：{stage["stage_timestamp"]}')
            if stage.get('ticket_time'):
                stage['ticket_timestamp'] = self.__infer_stage_time(stage['ticket_time'])
                logger.info(f'推断售票时间：{stage["ticket_timestamp"]}')
                
        
        return result
    