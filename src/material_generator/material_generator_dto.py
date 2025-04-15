from pydantic import BaseModel

class Material(BaseModel):
    text_material: str = 'Текст задания/лекционный материал/тест/список литературы'