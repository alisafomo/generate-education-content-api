# from datetime import datetime
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import os
import requests   
import time  
import json   
from src.database import models
from src.knowledge_base.knowledge_base_dto import Profession, KnowledgeArea, Skill
from src.analytics.analyser import analyse_vacancy
from sqlalchemy import func
from src.database.db import db_dependency
from fastapi import HTTPException


def update_profession_data(Profession, db):
    # it_roles_hh = get_roles('11')
    # id_profession = find_role(it_roles_hh, Profession.name_profession)
    # save_profession_to_db(db, id_profession, Profession.name_profession)
    # token = os.environ.get('HH_TOKEN')

    # vacancies_ids = get_vacancies_ids(id_profession, token, 20)

    # for vacancy_id in vacancies_ids:
    #     skills = get_vacancy_skills(vacancy_id, token)
    #     if skills != 'Нет навыков':
    #         save_vacancies_to_db(db, vacancy_id, skills, id_profession)
    
    analyse_vacancy(db, '124')




def delete_profession_data(profession_name, db):
    try:
        # Получаем объект профессии
        profession = db.query(models.Profession).filter_by(name_profession=profession_name.name_profession).first()
        
        if not profession:
            print(f"Профессия '{profession_name.name_profession}' не найдена.")
            return
        
        id_profession = profession.id_profession
        
        # Удаляем связанные записи в правильном порядке (сначала зависимые таблицы)
        
        # 1. Удаляем связи SkillByEducationalModule
        skill_ids = [skill.id_skill for skill in db.query(models.Skill.id_skill)
                    .filter_by(id_profession=id_profession).all()]
        
        if skill_ids:
            # Удаляем связи образовательных модулей с навыками
            db.query(models.SkillByEducationalModule)\
              .filter(models.SkillByEducationalModule.id_skill.in_(skill_ids))\
              .delete(synchronize_session=False)
            
            # Удаляем образовательные модули, связанные через эти навыки
            module_ids = [row[0] for row in 
                         db.query(models.SkillByEducationalModule.id_educational_module)
                         .filter(models.SkillByEducationalModule.id_skill.in_(skill_ids))
                         .distinct().all()]
            
            if module_ids:
                db.query(models.EducationalModule)\
                  .filter(models.EducationalModule.id_educational_module.in_(module_ids))\
                  .delete(synchronize_session=False)
        
        # 2. Удаляем образовательные модули, связанные через области знаний
        knowledge_area_ids = [ka.id_knowledge_area for ka in 
                            db.query(models.KnowledgeArea)
                            .filter_by(id_profession=id_profession).all()]
        
        if knowledge_area_ids:
            # Удаляем связи образовательных модулей
            db.query(models.SkillByEducationalModule)\
              .filter(models.SkillByEducationalModule.id_educational_module.in_(
                  db.query(models.EducationalModule.id_educational_module)
                  .filter(models.EducationalModule.id_knowledge_area.in_(knowledge_area_ids))
              )).delete(synchronize_session=False)
            
            # Удаляем сами модули
            db.query(models.EducationalModule)\
              .filter(models.EducationalModule.id_knowledge_area.in_(knowledge_area_ids))\
              .delete(synchronize_session=False)
        
        # 3. Удаляем вакансии
        db.query(models.Vacancy)\
          .filter_by(id_profession=id_profession)\
          .delete(synchronize_session=False)
        
        # 4. Удаляем навыки
        db.query(models.Skill)\
          .filter_by(id_profession=id_profession)\
          .delete(synchronize_session=False)
        
        # 5. Удаляем области знаний
        db.query(models.KnowledgeArea)\
          .filter_by(id_profession=id_profession)\
          .delete(synchronize_session=False)
        
        # 6. Удаляем саму профессию
        db.delete(profession)
        db.commit()
        
        print(f"Все данные для профессии '{profession_name.name_profession}' успешно удалены.")
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при удалении данных: {str(e)}")
        raise


def get_list_professions(db):
    professions = db.query(models.Profession.name_profession).all()
    print(professions) 

    result: list[Profession] = []
    for profession in professions:
        profession_obj = Profession(
            name_profession=profession[0] 
        )
        result.append(profession_obj)
    
    return result


def get_list_knowledge_areas(db, profession):
    knowledge_areas = db.query(models.KnowledgeArea.name_knowledge_area).\
        join(models.Profession, models.KnowledgeArea.id_profession == models.Profession.id_profession).\
        filter(models.Profession.name_profession == profession['profession']).\
        all()
    print(knowledge_areas)

    result: list[KnowledgeArea] = []
    for area in knowledge_areas:
        knowledge_area = KnowledgeArea(
            name_knowledge_area=area[0]
        )
        result.append(knowledge_area)
    return result


def get_list_skills(db, knowledge_area):
    skills = db.query(models.Skill.name_skill).\
        join(models.KnowledgeArea, models.Skill.id_knowledge_area == models.KnowledgeArea.id_knowledge_area).\
        filter(models.KnowledgeArea.name_knowledge_area == knowledge_area['knowledge_area']).\
        all()
    print(skills)  

    result: list[Skill] = []
    for skill in skills:
        skill_obj = Skill(
            name_skill=skill[0] 
        )
        result.append(skill_obj)
    
    return result

def get_access_token(client_id, client_secret):
    auth_url = "https://hh.ru/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"User-Agent": "myapp://auth (alisa.fomo@yandex.ru)"}
    
    try:
        response = requests.post(auth_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении токена: {e}")
        return None

def get_vacancy_skills(vacancy_id, access_token=None):
    """Получает ключевые навыки для конкретной вакансии."""
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    headers = {"User-Agent": "myapp://auth (alisa.fomo@yandex.ru)"}
    
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Извлекаем навыки и объединяем их в строку через запятую
        skills = [skill["name"] for skill in data.get("key_skills", [])]
        return ", ".join(skills) if skills else "Нет навыков"
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе вакансии {vacancy_id}: {e}")
        return None

def get_vacancies_ids(role_id, access_token=None, num_pages=1, per_page=100):
    base_url = "https://api.hh.ru/vacancies"
    vacancies_ids = []
    
    headers = {"User-Agent": "myapp://auth (alisa.fomo@yandex.ru)"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    # date_to = []
    # date_from = []
    # date_to.append(datetime.now().date())
    # date_to.append(datetime.now().date()- timedelta(days=182))
    # date_from.append(datetime.now().date() - timedelta(days=181))
    # date_from.append(datetime.now().date() - timedelta(days=365))

    for page in range(num_pages):
        params = {
            "professional_role": role_id,
            "area": 113,          
            "page": page,          
            "per_page": per_page
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            for vacancy in data.get("items", []):
                vacancies_ids.append(vacancy["id"])
            
            print(f"Страница {page + 1}: получено {len(data.get('items', []))} вакансий")
            time.sleep(0.5) 
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка на странице {page + 1}: {e}")
    
    return vacancies_ids

def get_roles(category: str):
    req = requests.get('https://api.hh.ru/professional_roles')
    data = req.content.decode()
    req.close()
    jsObj = json.loads(data)
    data = []
    for i in range(len(jsObj['categories'])):
        if len(jsObj['categories'][i]['roles']) != 0:
            for j in range(len(jsObj['categories'][i]['roles'])):
              data.append([jsObj['categories'][i]['id'],
                            jsObj['categories'][i]['name'],
                            jsObj['categories'][i]['roles'][j]['id'],
                            jsObj['categories'][i]['roles'][j]['name']])
    filtered_data_roles = [record for record in data if record[0] == category]
    dict_roles = {row[2]: row[3] for row in filtered_data_roles}
    print(dict_roles)
    return dict_roles


def find_role(dictionary, target_value):
    """Находит ключ по значению в словаре."""
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None 

def save_vacancies_to_db(db: Session, vacancy_id: int, skills: str, id_profession: int) -> Optional[models.Vacancy]:
    try:
        new_vacancy = models.Vacancy(
            id_vacancy=vacancy_id,
            key_skills=skills,
            id_profession=id_profession
        )
        
        db.add(new_vacancy)
        db.commit()
        db.refresh(new_vacancy)  
        
        return new_vacancy
    
    except Exception as e:
        db.rollback()  # Откатываем изменения в случае ошибки
        print(f"Ошибка при сохранении вакансии {vacancy_id}: {e}")
        return None
    
def save_profession_to_db(db: Session, id_profession: int, name_profession: str) -> models.Profession:
    try:
        # Проверяем, существует ли уже такая профессия
        existing = db.query(models.Profession).filter(
            (models.Profession.id_profession == id_profession) |
            (models.Profession.name_profession == name_profession)
        ).first()
        
        if existing:
            print(f"Профессия уже существует: ID {existing.id_profession} - {existing.name_profession}")
            return existing
            
        # Создаем новую запись
        new_profession = models.Profession(
            id_profession=id_profession,
            name_profession=name_profession
        )
        
        db.add(new_profession)
        db.commit()
        db.refresh(new_profession)
        return new_profession
    
    except Exception as e:
        db.rollback()
        print(f"Ошибка при сохранении профессии: {e}")
        return None
