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
    type: str = 'Введение в MongoDB'
    text: str = 'Какие из этих принципов относятся к REST?'
    options: list[dict] = [{'Stateless', True}]

class TaskMaterial(BaseModel):
    skills: str = 'mongodb, compass'
    text: str = 'Какие из этих принципов относятся к REST?'
    answer: str = 'Ссылка на материал'