from datetime import datetime
from src.database import models
from src.material_generator.material_generator_dto import EducationalModule, LectureMaterial, ReferenceMaterial, TestMaterial, TaskMaterial
from sqlalchemy import func
from src.database.db import db_dependency
from fastapi import HTTPException
from openai import OpenAI
import json
import os

def get_educational_modules(db, knowledge_area):
    pass

def get_lecture_material(db, user_prompt):
    skills = db.query(models.Skill.name_skill).\
        join(models.SkillByEducationalModule, models.Skill.id_skill == models.SkillByEducationalModule.id_skill).\
        join(models.EducationalModule, models.SkillByEducationalModule.id_educational_module == models.EducationalModule.id_educational_module).\
        filter(models.EducationalModule.name_educational_module == user_prompt['educational_module']).\
        all()
    list_skills = ', '.join([skill[0] for skill in skills])
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com")
    prompt = f"Тема модуля: {user_prompt['educational_module']}. Навыки, которые должен получить обучающийся: {list_skills}. Дополнительная информация: {user_prompt['additional_info']}"
    messages = [
        {"role": "system", "content": "Ты пишешь планы лекций для модуля электронного курса. Выводишь только json со структурой {lectures: [{title, skills: [], plan}]. Дополнительнцю информацию в вопросе считай приоритетной, если она есть. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3
            )
    result = json.loads(response.choices[0].message.content)
    lecture_materials: list[LectureMaterial] = []
    for lecture in result['lectures']:
        skills_str = ', '.join(lecture['skills'])
        material = LectureMaterial(
            title=lecture['title'],
            skills=skills_str,
            text=lecture['plan']
        )
        lecture_materials.append(material)
    return lecture_materials


def get_references(db, user_prompt):
    skills = db.query(models.Skill.name_skill).\
        join(models.SkillByEducationalModule, models.Skill.id_skill == models.SkillByEducationalModule.id_skill).\
        join(models.EducationalModule, models.SkillByEducationalModule.id_educational_module == models.EducationalModule.id_educational_module).\
        filter(models.EducationalModule.name_educational_module == user_prompt['educational_module']).\
        all()
    list_skills = ', '.join([skill[0] for skill in skills])
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com")
    prompt = f"Тема модуля: {user_prompt['educational_module']}. Навыки, которые должен получить обучающийся: {list_skills}. Дополнительная информация: {user_prompt['additional_info']}"
    messages = [
        {"role": "system", "content": "Ты даёшь ссылки на реально существующие книги и интернет-ресурсы на русском языке. Выводишь только json со структурой {ref: [{title, skills: [], link}]. title - название книги или интернет-ресурса с авторами, link - работающая ссылка. Дополнительнцю информацию в вопросе считай приоритетной, если она есть. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3
            )
    result = json.loads(response.choices[0].message.content)
    ref_materials: list[ReferenceMaterial] = []
    for ref in result['ref']:
        skills_str = ', '.join(ref['skills'])
        material = ReferenceMaterial(
            title=ref['title'],
            skills=skills_str,
            link=ref['link']
        )
        ref_materials.append(material)
    return ref_materials


def get_test(db, prompt):
    pass


def get_task(db, prompt):
    pass
