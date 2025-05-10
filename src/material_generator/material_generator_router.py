from fastapi import APIRouter, Depends, Query
from src.material_generator.material_generator_dto import EducationalModule, LectureMaterial, ReferenceMaterial, TestMaterial, TaskMaterial
from src.auth import get_api_key
from src.material_generator import material_generator_service
from src.database.db import db_dependency


router = APIRouter(
    prefix='/api',
    tags=['Генерация материала'],
)


@router.get('/educational_modules', summary='Получение списка образовательных модулей по области знаний', 
            description='Получаем список образовательных модулей.')
async def get_educational_modules(db: db_dependency, KnowledgeArea: str = Query(...), api_key: str = Depends(get_api_key)) -> list[EducationalModule]:
    return material_generator_service.get_educational_modules(db, {"knowledge_area": KnowledgeArea})

@router.get('/lecture_material', summary='Получение плана лекционного материала', 
            description='Получаем JSON с планом лекционного материала.')
async def get_lecture_material(db: db_dependency, EducationalModule: str = Query(...), AdditionalInfo: str = Query(''), api_key: str = Depends(get_api_key)) -> list[LectureMaterial]:
    return material_generator_service.get_lecture_material(db, {"educational_module": EducationalModule, "additional_info": AdditionalInfo})


@router.get('/references', summary='Получение списка литературы', 
            description='Получаем JSON со списком литературы.')
async def get_references(db: db_dependency, EducationalModule: str = Query(...), AdditionalInfo: str = Query(''), api_key: str = Depends(get_api_key)) -> list[ReferenceMaterial]:
    return material_generator_service.get_references(db, {"educational_module": EducationalModule, "additional_info": AdditionalInfo})


@router.get('/test', summary='Получение тестового задания', 
            description='Получаем JSON с тестовыми заданиями.')
async def get_test(db: db_dependency, EducationalModule: str = Query(...), AdditionalInfo: str = Query(''), api_key: str = Depends(get_api_key)) -> list[TestMaterial]:
    return material_generator_service.get_test(db, {"educational_module": EducationalModule, "additional_info": AdditionalInfo})


@router.get('/task', summary='Получение задания в свободной форме', 
            description='Получаем JSON с заданиями в свободной форме.')
async def get_task(db: db_dependency, EducationalModule: str = Query(...), AdditionalInfo: str = Query(''), api_key: str = Depends(get_api_key)) -> list[TaskMaterial]:
    return material_generator_service.get_task(db, {"educational_module": EducationalModule, "additional_info": AdditionalInfo})
