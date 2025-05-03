# from datetime import datetime
# from src.database import models
# from src.analytics.analytics_dto import ScenarioStatistic, UserScenarioVisit
# from sqlalchemy import func
# from src.database.db import db_dependency
# from fastapi import HTTPException


# def save_user_scenario_visits(user_scenario_visit: UserScenarioVisit, db: db_dependency):
#     try:
#         info = user_scenario_visit.model_dump()
#         data = models.Statistics(user_id=info.get('user_id'),
#                                  visit_date_time=datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
#                                  name_scenario=info.get('name_scenario'))
#         db.add(data)
#         db.commit()

#     except Exception as error:
#         db.rollback()
#         raise HTTPException(status_code=520, detail=str(error))


# def get_count_users_by_scenarios(date_start: str, date_end: str, db: db_dependency):
#     try:
#         date_start = datetime.strptime(date_start, '%d.%m.%Y')
#         date_end = datetime.strptime(date_end, '%d.%m.%Y')
#         results = []
#         data = db.query(
#             models.Statistics.name_scenario, 
#             func.count(models.Statistics.name_scenario)
#         ).filter(
#             func.to_timestamp(models.Statistics.visit_date_time, '%d.%m.%Y %H:%M:%S') >= date_start, 
#             func.to_timestamp(models.Statistics.visit_date_time, '%d.%m.%Y %H:%M:%S') <= date_end
#         ).group_by(models.Statistics.name_scenario).all()
#         for row in data:
#             scenario_statistic = ScenarioStatistic(name_scenario=row[0],
#                                                 count_visits=row[1])
#             results.append(scenario_statistic)
#         return results
    
#     except Exception as error:
#         raise HTTPException(status_code=520, detail=str(error))
