from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Artist(Base):
    __tablename__ = 'artists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    weibo_uid = Column(String, nullable=False, unique=True)
    stages = relationship("Stage", back_populates="artist")  # 一个艺人可以有多个演出

class Stage(Base):
    __tablename__ = 'stages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    show_time = Column(DateTime, nullable=False)
    details = Column(JSON)
    weibo_url = Column(String)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    artist = relationship("Artist", back_populates="stages")  # 一个演出只属于一个艺人