from datetime import datetime

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column[int](Integer, primary_key=True)
    telegram_id: Column[int] = Column(BigInteger, unique=True)
    username = Column[str](String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    translation_mode = Column[str](String, default="en-ru")

    words = relationship("UserWords", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievements", back_populates="user", cascade="all, delete-orphan")
    statistics = relationship("UserStatistics", back_populates="user", uselist=False, cascade="all, delete-orphan")
    logins = relationship("DateLogins", back_populates="user", cascade="all, delete-orphan")

class Words(Base):
    __tablename__ = 'words'

    id = Column[int](Integer, primary_key=True)
    word: Column[str] = Column[str](String(100),nullable=False)
    translation = Column[str](String(100), nullable=False)

    users_assoc = relationship("UserWords", back_populates="word")


class UserWords(Base):
    __tablename__ = 'user_words'

    wordId: Column[int] = Column(Integer, ForeignKey('words.id'), primary_key=True)
    userId: Column[int] = Column(Integer, ForeignKey("users.id"), primary_key=True)

    word = relationship("Words", back_populates="users_assoc")
    user = relationship("Users", back_populates="words")


class Achievements(Base):
    __tablename__ = 'achievements'

    id: Column[int] = Column[int](Integer, primary_key=True)
    name = Column[str](String(100), nullable=False)
    description = Column[str](String, nullable=False)
    achievement_type: Column[str] = Column[str](String,nullable=False)
    goal: Column[str] = Column[str](Integer, nullable=False)

    users_earned = relationship("UserAchievements", back_populates="achievement")

class UserAchievements(Base):
    __tablename__= 'user_achievement'

    achievement_id: Column[int] = Column[int](Integer, ForeignKey('achievements.id'), primary_key= True)
    user_id: Column[int] = Column[int](Integer, ForeignKey('users.id'), primary_key=True)
    achieve_date = Column(DateTime)

    achievement = relationship("Achievements", back_populates="users_earned")
    user = relationship("Users", back_populates='achievements')

class UserStatistics(Base):
    __tablename__ = 'statistics'

    userId: Column[int] = Column[int](Integer, ForeignKey('users.id'), primary_key=True)
    total_words = Column[int](Integer, default=0)
    total_correct = Column[int](Integer, default=0)
    total_wrong = Column[int](Integer, default=0)
    current_streak = Column[int](Integer, default=0)
    max_streak = Column[int](Integer, default=0)

    user = relationship("Users", back_populates="statistics")

class DateLogins(Base):
    __tablename__ = 'date_logins'

    userId: Column[int] = Column[int](Integer, ForeignKey("users.id"), primary_key=True)
    date_login: Column[datetime] = Column(DateTime, nullable=False, primary_key=True)

    user = relationship("Users", back_populates="logins")
