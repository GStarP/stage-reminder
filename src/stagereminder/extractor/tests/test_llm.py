import json
import pytest
import os
from pathlib import Path
from stagereminder.extractor.llm import LLMExtractor
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

@pytest.fixture
def example_weibos():
    """加载示例微博数据"""
    json_path = Path(__file__).parent / "exmaple_weibo_info.json"
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_extract_stage_info(example_weibos):
    """测试从示例微博数据中提取演出信息"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    extractor = LLMExtractor(api_key)
    
    # 遍历所有微博
    for weibo in example_weibos["weibos"]:
        result = await extractor.extract_stage_info(weibo["text"])
        
        # 如果是演出预告，打印详细信息
        if result.get("is_preview"):
            print(f"\n发现演出预告 (微博ID: {weibo['id']}):")
            print(json.dumps(result, ensure_ascii=False, indent=2))