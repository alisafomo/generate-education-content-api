from pydantic import BaseModel

class EducationalModule(BaseModel):
    educational_module: str = 'Введение в MongoDB'

class LectureMaterial(BaseModel):
    skills: str = 'mongodb, compass'
    title: str = 'Введение в MongoDB'
    text: str = 'Текст лекции'

class ReferenceMaterial(BaseModel):
    skills: str = 'mongodb, compass'
    title: str = 'Введение в MongoDB'
    link: str = 'Ссылка на материал'

class TestMaterial(BaseModel):
    skills: str = 'mongodb, compass'
    title: str = 'Введение в MongoDB'
    link: str = 'Ссылка на материал'

class TaskMaterial(BaseModel):
    skills: str = 'mongodb, compass'
    title: str = 'Введение в MongoDB'
    link: str = 'Ссылка на материал'