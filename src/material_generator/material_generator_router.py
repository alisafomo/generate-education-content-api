from fastapi import APIRouter, Depends
from src.material_generator.material_generator_dto import Material
from src.auth import get_api_key
from src.knowledge_base.knowledge_base_dto import Skill
from src.material_generator import material_generator_service
from src.database.db import db_dependency


router = APIRouter(
    prefix='/api',
    tags=['Генерация материала'],
)


@router.get('/lecture_material', summary='Получение лекционного материала', 
            description='Получаем JSON лекционным материалом по навыку.')
async def get_lecture_material(skill: Skill,db: db_dependency, api_key: str = Depends(get_api_key)) -> Material:
    return material_generator_service.get_lecture_material(skill, db)


@router.get('/references', summary='Получение списка литературы', 
            description='Получаем JSON со списком литературы по навыку.')
async def get_references(skill: Skill, db: db_dependency, api_key: str = Depends(get_api_key)) -> Material:
    return material_generator_service.get_references(skill, db)


@router.get('/test', summary='Получение тестового задания', 
            description='Получаем JSON с тестовыми заданиями по навыку.')
async def get_test(skill: Skill, db: db_dependency, api_key: str = Depends(get_api_key)) -> Material:
    return material_generator_service.get_test(skill, db)


@router.get('/task', summary='Получение задания в свободной форме', 
            description='Получаем JSON с заданиями в свободной форме по навыку.')
async def get_task(skill: Skill, db: db_dependency, api_key: str = Depends(get_api_key)) -> Material:
    return material_generator_service.get_task(skill, db)
