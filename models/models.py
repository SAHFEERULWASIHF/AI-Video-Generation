from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy.orm import relationship, declarative_base
import datetime
import enum

Base = declarative_base()

class ReelStatus(enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    EDITING = "editing"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    POSTED = "posted"
    FAILED = "failed"

class AccountType(enum.Enum):
    GOOGLE = "google"
    INSTAGRAM = "instagram"

class Reel(Base):
    __tablename__ = "reels"

    id = Column(Integer, primary_key=True)
    topic = Column(String, nullable=False)
    script = Column(Text)
    status = Column(Enum(ReelStatus), default=ReelStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    video_path = Column(String)
    instagram_caption = Column(Text)

    scenes = relationship("Scene", back_populates="reel", cascade="all, delete-orphan")

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(Integer, primary_key=True)
    reel_id = Column(Integer, ForeignKey("reels.id"))
    scene_number = Column(Integer)
    duration = Column(Integer)
    dialogue = Column(Text)
    visual_prompt = Column(Text)
    first_frame_prompt = Column(Text)
    last_frame_prompt = Column(Text)
    video_generation_prompt = Column(Text)

    image_path = Column(String)
    video_path = Column(String)
    status = Column(String) # e.g., "pending", "completed", "failed"

    reel = relationship("Reel", back_populates="scenes")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    account_type = Column(Enum(AccountType))
    recovery_email = Column(String)
    profile_path = Column(String) # Playwright persistent profile path

    daily_usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = Column(Integer, primary_key=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    provider = Column(String) # "gemini", "veo"
    status = Column(String)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PublishLog(Base):
    __tablename__ = "publish_logs"

    id = Column(Integer, primary_key=True)
    reel_id = Column(Integer, ForeignKey("reels.id"))
    platform = Column(String, default="instagram")
    status = Column(String)
    post_id = Column(String)
    url = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
