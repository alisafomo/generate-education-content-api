from pydantic import BaseModel

class Profession(BaseModel):
    name_profession: str = 'Аналитик'

class KnowledgeArea(BaseModel):
    name_knowledge_area: str = 'Бизнес-процессы'

class Skill(BaseModel):
    name_skill: str = 'Управление проектами'

