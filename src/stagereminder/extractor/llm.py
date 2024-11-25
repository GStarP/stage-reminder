from openai import AsyncOpenAI
from typing import Dict
import json

class LLMExtractor:
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(base_url="https://api.deepseek.com/v1", api_key=api_key)
        self.system_prompt = """
你是一个专门分析微博内容的助手。你的任务是从微博文本中提取演出相关信息。

请注意区分以下情况：
1. 演出预告：包含未来将要举办的演出信息，通常会提到售票时间、票价等关键信息
2. 演出回顾：描述已经结束的演出，通常是感谢、分享照片等内容

只有对于演出预告，才需要提取并返回以下信息：
- stage_name: 演出名称 (str)
- stage_time: 演出时间 (datetime)
- stage_location: 演出地点 (str)
- ticket_time: 售票时间 (datetime)
- ticket_price: 票价信息 (str)
- ticket_platform: 售票平台 (str)
- artists: 参演者 (str[])
- organizer: 主办方 (str)
- description: 演出内容描述 (str)
- slogan: 宣传语 (str)

其中，时间应该为 yyyy-MM-dd hh:mm 的形式，如果缺少时分秒信息可以改为 yyyy-MM-dd 的形式，如果缺少日期信息可以改为 yyyy-MM 的形式，如果连年月信息都没有则视为没有这一字段。

如果是演出回顾或者与演出无关的内容，请以JSON格式返回提取结果：
{
    "is_preview": false,
    "reason": "这是一条演出回顾/与演出无关的微博"
}

如果是演出预告，请返回：
{
    "is_preview": true,
    "stage_info": {
        // 上述字段，未提及的字段可以省略
    }
}
"""

    async def extract_stage_info(self, post_text: str) -> Dict:
        """
        从推文中提取演出相关信息

        Args:
            text: 推文内容

        Returns:
            提取的演出信息或空结果
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请分析以下推文内容：\n\n{post_text}"}
        ]
        
        print(f'正在分析推文：{post_text[:10]}')
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        # 将返回的 JSON 字符串解析为 Python 字典
        return json.loads(response.choices[0].message.content)
    