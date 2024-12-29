import json
import pytest
import os
from pathlib import Path
from stagereminder.parser.stage_parser import StageParser
from dotenv import load_dotenv
from stagereminder.logger import logger


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
    parser = StageParser(api_key)
    
    all_stage_info = []
    # 遍历所有微博
    for weibo in example_weibos:
        result = await parser.parse_weibo(weibo)
        if result.get("found"):
            all_stage_info.append(result)
    
    logger.info(f"所有演出预告信息: {all_stage_info}")