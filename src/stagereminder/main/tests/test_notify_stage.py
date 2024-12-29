import pytest
from stagereminder.main.notify_stage import _generate_notify_content
from stagereminder.logger import logger

@pytest.mark.asyncio
async def test_notify_stage():
    """测试通知演出信息"""
    content = _generate_notify_content()
    logger.info(content)