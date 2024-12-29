from pathlib import Path
from sqlalchemy import create_engine
from stagereminder.main.models import Base, Artist
from stagereminder.logger import logger
from sqlalchemy.orm import sessionmaker

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
        # 插入默认数据
        session = sessionmaker(bind=engine)()
        session.add(Artist(name="银临", weibo_uid="2266537042"))
        session.add(Artist(name="Winky诗", weibo_uid="1438245880"))
        session.add(Artist(name="贰婶", weibo_uid="1734324972"))
        session.add(Artist(name="不才", weibo_uid="2026955024"))
        session.add(Artist(name="李常超", weibo_uid="2797470872"))
        session.commit()
        session.close()

        logger.info(f"数据库初始化成功: {db_path}")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_db()