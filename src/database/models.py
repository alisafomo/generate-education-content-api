from sqlalchemy import Column, Integer, String
from src.database.db import Base


class Profession(Base):
    __tablename__ = 'profession'

    id_profession = Column(Integer, primary_key=True, autoincrement=True)
    name_profession = Column(String)

class Skill(Base):
    __tablename__ = 'skill'

    id_skill = Column(Integer, primary_key=True, autoincrement=True)
    name_skill = Column(String)

class KnowledgeArea(Base):
    __tablename__ = 'knowledge_area'

    id_knowledge_area = Column(Integer, primary_key=True, autoincrement=True)
    name_knowledge_area = Column(String)
    
class Vacancy(Base):
    __tablename__ = 'vacancy'

    id_vacancy = Column(Integer, primary_key=True)
    key_skills = Column(String)
    id_profession = Column(Integer)

class SkillByProfession(Base):
    __tablename__ = 'skill_by_profession'

    id_skill = Column(Integer, primary_key=True)
    id_profession = Column(Integer, primary_key=True)

class SkillByKnowledgeArea(Base):
    __tablename__ = 'skill_by_knowledge_area'

    id_skill = Column(Integer, primary_key=True)
    id_knowledge_area = Column(Integer, primary_key=True)

class EducationalModule(Base):
    __tablename__ = 'educational_module'

    id_educational_module = Column(Integer, primary_key=True, autoincrement=True)
    name_educational_module = Column(String)
    requirements = Column(String)
    id_skill = Column(Integer)
    id_knowledge_area = Column(Integer)
