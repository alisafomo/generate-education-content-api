from fastapi import APIRouter, Depends
from src.analytics.analytics_dto import ScenarioStatistic, UserScenarioVisit
from src.auth import get_api_key
from src.analytics import analytics_service
from src.database.db import db_dependency


router = APIRouter(
    prefix='/api',
    tags=['Аналитика'],
)


@router.post('/analytics', summary='Сохранение информации о посещении сценария пользователями')
async def save_user_scenario_visits(user_scenario_visit: UserScenarioVisit, db: db_dependency, api_key: str = Depends(get_api_key)):
    return analytics_service.save_user_scenario_visits(user_scenario_visit, db)


@router.get('/analytics', summary='Получение количества посещений каждого сценария', 
            description='Получаем JSON с списком сценариев и количеством их посещений пользователями.')
async def get_count_users_by_scenarios(db: db_dependency, api_key: str = Depends(get_api_key), date_start: str = '01.01.2025', date_end: str = '25.01.2025') -> list[ScenarioStatistic]:
    return analytics_service.get_count_users_by_scenarios(date_start, date_end, db)
