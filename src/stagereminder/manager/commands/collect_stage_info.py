import os
import asyncio
from stagereminder.manager.service import StageReminderService
from stagereminder.logger import logger
from dotenv import load_dotenv

async def main():
    # 加载环境变量
    load_dotenv()
    
    # 初始化服务
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("未找到 DEEPSEEK_API_KEY 环境变量")
        return
        
    service = StageReminderService(llm_api_key=api_key)
    
    try:
        logger.info("开始收集演出信息...")
        await service.update_stages()
        logger.info("演出信息收集完成")
        
        # 打印收集到的信息
        response = await service.handle_query_message()
        logger.info(f"{response}")
        
    except Exception as e:
        logger.error(f"收集演出信息时发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())