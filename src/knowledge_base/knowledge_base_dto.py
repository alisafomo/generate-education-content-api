from pydantic import BaseModel

class Profession(BaseModel):
    name_profession: str = 'Тестировщик'

class KnowledgeArea(BaseModel):
    name_knowledge_area: str = 'Бизнес-процессы'

class Skill(BaseModel):
    name_skill: str = 'Управление проектами'

