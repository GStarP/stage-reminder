import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Artist, Stage

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_url="sqlite:///db/stagereminder.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_all_artists(self):
        """获取所有关注的艺人"""
        session = self.Session()
        try:
            artists = session.query(Artist).all()
            return artists
        except SQLAlchemyError as e:
            logger.error(f"Error getting artists: {e}")
            return []
        finally:
            session.close()

    def add_or_update_stage(self, artist_id: int, stage_data: dict) -> bool:
        """添加或更新演出信息"""
        session = self.Session()
        try:
            # 检查艺人是否存在
            artist = session.query(Artist).filter_by(id=artist_id).first()
            if not artist:
                logger.error(f"Artist with id {artist_id} not found")
                return False

            # 检查是否已存在相同演出
            existing_stage = (
                session.query(Stage)
                .filter_by(
                    artist_id=artist_id,
                    name=stage_data['name'],
                    show_time=stage_data['show_time']
                )
                .first()
            )

            if existing_stage:
                logger.info(f"Stage already exists: {stage_data['name']}")
                return False

            # 创建新的演出记录
            new_stage = Stage(
                name=stage_data['name'],
                show_time=stage_data['show_time'],
                details=stage_data.get('details', {}),
                weibo_url=stage_data.get('weibo_url'),
                artist_id=artist_id
            )
            session.add(new_stage)
            session.commit()
            
            logger.info(f"Added new stage: {stage_data['name']} for artist {artist.name}")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Error adding/updating stage: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_artist_stages(self, artist_id: int):
        """获取指定艺人的所有未开始的演出信息"""
        session = self.Session()
        try:
            now = datetime.now()
            stages = (
                session.query(Stage)
                .filter(
                    Stage.artist_id == artist_id,
                    # @DEBUG 暂时不管时间
                    # Stage.show_time > now
                )
                .order_by(Stage.show_time)
                .all()
            )
            return stages
        except SQLAlchemyError as e:
            logger.error(f"Error getting stages for artist {artist_id}: {e}")
            return []
        finally:
            session.close()