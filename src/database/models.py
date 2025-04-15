from sqlalchemy import BigInteger, Column, Integer, String
from src.database.db import Base


class User(Base):
    __tablename__ = 'career_guidance_users'

    telegram_id = Column(BigInteger, primary_key=True)
    registration_number = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    phone = Column(String)
    university = Column(String)
    faculty = Column(String)
    course = Column(String)
    date = Column(String)
    
class Statistics(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    visit_date_time = Column(String)
    name_scenario = Column(String)
