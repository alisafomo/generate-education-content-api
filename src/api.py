from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import models
from src.database.db import engine
from src.material_generator import material_generator_router
from src.knowledge_base import knowledge_base_router


app = FastAPI(title='Generator Education Material API',
              description='API сервисов для генерации учебного материала по данным вакансий', version='0.1')
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(material_generator_router.router)
app.include_router(knowledge_base_router.router)

