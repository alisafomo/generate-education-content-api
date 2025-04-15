from fastapi import APIRouter, Depends
from src.auth import get_api_key
from src.knowledge_base import knowledge_base_service
from src.knowledge_base.knowledge_base_dto import Profession, KnowledgeArea, Skill
from src.database.db import db_dependency


router = APIRouter(
    prefix='/api',
    tags=['Управление базой знаний'],
)


@router.post('/profession_data', summary='Загрузка данных вакансий с hh.ru по профессии')
async def update_profession_data(profession: Profession, db: db_dependency, api_key: str = Depends(get_api_key)):
    return knowledge_base_service.update_profession_data(profession, db)


@router.delete('/profession_data', summary='Удаление данных вакансий по профессии')
async def delete_profession_data(profession: Profession, db: db_dependency, api_key: str = Depends(get_api_key)):
    return knowledge_base_service.delete_profession_data(profession, db)


@router.get('/list_professions', summary='Получение списка профессий', 
            description='Получаем JSON с списком профессий, вакансии которых загружены в базу данных.')
async def get_list_professions(db: db_dependency, api_key: str = Depends(get_api_key)) -> list[Profession]:
    return knowledge_base_service.get_list_professions(db)


@router.get('/list_knowledge_areas', summary='Получение списка областей знаний по профессии', 
            description='Получаем JSON с списком областей знаний, которые необходимо освоить для работы по профессии.')
async def get_list_knowledge_areas(profession: Profession, db: db_dependency, api_key: str = Depends(get_api_key)) -> list[KnowledgeArea]:
    return knowledge_base_service.get_list_knowledge_areas(profession, db)


@router.get('/list_skills', summary='Получение списка навыков для области знаний', 
            description='Получаем JSON с списком навыков для области знаний.')
async def get_list_skills(knowledge_area: KnowledgeArea, db: db_dependency, api_key: str = Depends(get_api_key)) -> list[Skill]:
    return knowledge_base_service.get_list_skills(knowledge_area, db)
