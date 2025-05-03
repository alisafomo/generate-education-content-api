from pydantic import BaseModel

class EducationalModule(BaseModel):
    educational_module: str = 'Введение в MongoDB'

class Material(BaseModel):
    text_material: str = 'Текст задания/лекционный материал/тест/список литературы'