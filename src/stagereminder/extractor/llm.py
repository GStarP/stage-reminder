from openai import AsyncOpenAI
from typing import Dict, Optional
import json
from stagereminder.logger import logger

class LLMExtractor:
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(base_url="https://api.deepseek.com/v1", api_key=api_key)
        self.system_prompt = """
## 角色
你是一个专门分析微博内容的助手。你的任务是从微博内容中提取演出预告信息。

## 任务
首先判断微博内容是否包含演出预告信息，如果包含，尝试从中提取演出预告信息，字段如下：
- stage_name: 演出名称 (str)(required)
- stage_time: 演出时间 (datetime)(required)
- stage_location: 演出地点 (str)(required)
- ticket_time: 售票时间 (datetime)
- ticket_price: 票价信息 (str)
- ticket_platform: 售票平台 (str)
- artists: 参演者 (str)
- organizer: 主办方 (str)
- description: 演出内容描述 (str)

## 注意事项
在提取演出预告信息时，请牢记以下注意事项：
- 即使微博内容包含部分演出相关信息，也不一定是演出预告信息，还有可能是演出结束后的回顾，请仔细甄别。我给出的建议是，当微博内容包含演出时间和演出地点，且具有明显的“预告”性质时，才认为其包含演出预告信息。
- 演出时间和售票时间：
  - 应该是单个时间，而非时间范围，如果有识别出一个时间范围，请使用其开始时间作为演出时间。
  - 如果提取到的时间信息没有包含年份，则认为是今年。
  - 时间信息应该尽可能详细，最理想的格式为"yyyy-MM-dd hh:mm"，如果缺少部分信息也可以改为"yyyy-MM-dd hh"/"yyyy-MM-dd"/"yyyy-MM"的格式。
- 演出地点不一定是一个物理地点，你应该先判断演出是否为线上演出，如果是线上演出，则演出地点更可能是线上平台。

## 输出格式
请以JSON格式输出，字段如下：
- found: 是否找到演出预告信息 (bool)
- stage_info: 演出预告信息 (Dict)

如果判断出此条微博内容中不包含演出预告信息，或者你无法从微博内容中提取出有效的演出预告信息，found为False，stage_info为空字典。
反之，found为True，stage_info为提取到的演出预告信息。
"""

    async def extract_stage_info(self, weibo_text: str) -> Optional[Dict]:
        """
        从微博内容中提取演出相关信息

        Args:
            weibo_text: 微博内容

        Returns:
            提取的演出预告信息或空结果
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请分析以下微博内容：\n\n{weibo_text}"}
        ]
        
        logger.info(f'正在分析推文：{weibo_text}')
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0,
            response_format={ "type": "json_object" }
        )

        result = json.loads(response.choices[0].message.content)
        logger.info(f'分析完成：{result}')
        
        return result
    