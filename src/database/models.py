from sqlalchemy import Column, Integer, String
from src.database.db import Base


class Profession(Base):
    __tablename__ = 'profession'

    id_profession = Column(Integer, primary_key=True, autoincrement=True)
    name_profession = Column(String)

class Skill(Base):
    __tablename__ = 'skill'

    id_skill = Column(Integer, primary_key=True, autoincrement=True)
    id_profession = Column(Integer)
    name_skill = Column(String)
    id_knowledge_area = Column(Integer)

class KnowledgeArea(Base):
    __tablename__ = 'knowledge_area'

    id_knowledge_area = Column(Integer, primary_key=True, autoincrement=True)
    name_knowledge_area = Column(String)
    id_profession = Column(Integer)
    
class Vacancy(Base):
    __tablename__ = 'vacancy'

    id_vacancy = Column(Integer, primary_key=True)
    key_skills = Column(String)
    id_profession = Column(Integer)

class EducationalModule(Base):
    __tablename__ = 'educational_module'

    id_educational_module = Column(Integer, primary_key=True, autoincrement=True)
    name_educational_module = Column(String)
    requirements = Column(String)
    id_knowledge_area = Column(Integer)

class SkillByEducationalModule(Base):
    __tablename__ = 'skill_by_educational_module'
    
    id_educational_module = Column(Integer, primary_key=True)
    id_skill = Column(Integer, primary_key=True)

