# src/stagereminder/manager/commands/init_db.py

import os
from pathlib import Path
from sqlalchemy import create_engine
from stagereminder.manager.models import Base
from stagereminder.logger import logger

def init_db():
    # 确保 db 目录存在
    db_dir = Path("db")
    db_dir.mkdir(exist_ok=True)
    
    # 创建数据库连接
    db_path = db_dir / "stagereminder.db"
    engine = create_engine(f"sqlite:///{db_path}")
    
    try:
        # 创建所有表
        Base.metadata.create_all(engine)
        logger.info(f"数据库初始化成功: {db_path}")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_db()