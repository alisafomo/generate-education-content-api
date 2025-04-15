from datetime import datetime
from src.database import models
from src.knowledge_base.knowledge_base_dto import Profession, KnowledgeArea, Skill
from sqlalchemy import func
from src.database.db import db_dependency
from fastapi import HTTPException


def update_profession_data(profession, db):
    pass


def delete_profession_data(profession, db):
    pass


def get_list_professions(db):
    pass


def get_list_knowledge_areas(profession, db):
    pass


def get_list_skills(knowledge_area, db):
    pass
