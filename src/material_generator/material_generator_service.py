from src.database import models
from src.material_generator.material_generator_dto import EducationalModule, LectureMaterial, ReferenceMaterial, TestMaterial, TaskMaterial
from openai import OpenAI
import json
import os
import requests
from lxml import etree
import time

def get_educational_modules(db, area):
    educational_modules = db.query(models.EducationalModule.name_educational_module).\
        join(models.KnowledgeArea, models.EducationalModule.id_knowledge_area == models.KnowledgeArea.id_knowledge_area).\
        filter(models.KnowledgeArea.name_knowledge_area == area['knowledge_area']).\
        all()
    print(educational_modules)

    result: list[EducationalModule] = []
    for module in educational_modules:
        ed_module = EducationalModule(
            educational_module=module[0]
        )
        result.append(ed_module)
    
    return result

def get_lecture_material(db, user_prompt):
    skills = db.query(models.Skill.name_skill).\
        join(models.SkillByEducationalModule, models.Skill.id_skill == models.SkillByEducationalModule.id_skill).\
        join(models.EducationalModule, models.SkillByEducationalModule.id_educational_module == models.EducationalModule.id_educational_module).\
        filter(models.EducationalModule.name_educational_module == user_prompt['educational_module']).\
        all()
    list_skills = ', '.join([skill[0] for skill in skills])
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com")
    prompt = f"Тема модуля: {user_prompt['educational_module']}. Навыки, которые должен получить обучающийся: {list_skills}. Дополнительная информация: {user_prompt['additional_info']}"
    messages = [
        {"role": "system", "content": "Ты пишешь планы лекций для модуля электронного курса на русском языке. Выводишь только json со структурой {lectures: [{title, skills: [], plan}]. Дополнительнцю информацию в вопросе считай приоритетной, если она есть. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=1.2
            )
    result = json.loads(response.choices[0].message.content)
    lecture_materials: list[LectureMaterial] = []
    for lecture in result['lectures']:
        skills_str = ', '.join(lecture['skills'])
        material = LectureMaterial(
            title=lecture['title'],
            skills=skills_str,
            text=lecture['plan']
        )
        lecture_materials.append(material)
    return lecture_materials


def get_references(db, user_prompt):
    skills = db.query(models.Skill.name_skill).\
        join(models.SkillByEducationalModule, models.Skill.id_skill == models.SkillByEducationalModule.id_skill).\
        join(models.EducationalModule, models.SkillByEducationalModule.id_educational_module == models.EducationalModule.id_educational_module).\
        filter(models.EducationalModule.name_educational_module == user_prompt['educational_module']).\
        all()
    list_skills = ', '.join([skill[0] for skill in skills])
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com/")
    prompt = f"Тема модуля: {user_prompt['educational_module']}. Навыки, которые должен получить обучающийся: {list_skills}. Дополнительная информация: {user_prompt['additional_info']}"
    messages = [
        {"role": "system", "content": "Ты даёшь ссылки на реально существующие книги и интернет-ресурсы на русском языке. Выводишь только json со структурой {ref: [{title, skills: [], link}]. title - название книги или интернет-ресурса с авторами, link - работающая ссылка. Дополнительнцю информацию в вопросе считай приоритетной, если она есть. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=1.2
            )
    result = json.loads(response.choices[0].message.content)
    ref_materials: list[ReferenceMaterial] = []
    for ref in result['ref']:
        skills_str = ', '.join(ref['skills'])
        search_link = yandex_search_first_link(ref['title'])
        print(search_link)
        material = ReferenceMaterial(
            title=ref['title'],
            skills=skills_str,
            link=search_link
        )
        ref_materials.append(material)
    return ref_materials


def get_test(db, user_prompt):
    skills = db.query(models.Skill.name_skill).\
        join(models.SkillByEducationalModule, models.Skill.id_skill == models.SkillByEducationalModule.id_skill).\
        join(models.EducationalModule, models.SkillByEducationalModule.id_educational_module == models.EducationalModule.id_educational_module).\
        filter(models.EducationalModule.name_educational_module == user_prompt['educational_module']).\
        all()
    list_skills = ', '.join([skill[0] for skill in skills])
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com/")
    prompt = f"Тема модуля: {user_prompt['educational_module']}. Навыки, которые должен получить обучающийся: {list_skills}. Дополнительная информация: {user_prompt['additional_info']}"
    messages = [
        {"role": "system", "content": "Ты пишешь тестовые задания по теме и навыкам на русском языке. Выводишь только json со структурой {questions : [{skills: [], type, text, options: [{text, isCorrect}]}]}. type может быть single_choice, multiple_choice и true_false (по умолчанию single_choice), text - текст вопроса, options - варианты ответа (по умолчанию 4 штуки). Количество заданий 1 штука. Дополнительнцю информацию в вопросе считай приоритетной, если она есть. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=1.2
            )
    result = json.loads(response.choices[0].message.content)
    print(result)
    test_materials: list[TestMaterial] = []
    for question in result['questions']:
        skills_str = ', '.join(question['skills'])
        material = TestMaterial(
            text=question['text'],
            skills=skills_str,
            type=question['type'],
            options=question['options'],
        )
        test_materials.append(material)
    return test_materials


def get_task(db, user_prompt):
    skills = db.query(models.Skill.name_skill).\
        join(models.SkillByEducationalModule, models.Skill.id_skill == models.SkillByEducationalModule.id_skill).\
        join(models.EducationalModule, models.SkillByEducationalModule.id_educational_module == models.EducationalModule.id_educational_module).\
        filter(models.EducationalModule.name_educational_module == user_prompt['educational_module']).\
        all()
    list_skills = ', '.join([skill[0] for skill in skills])
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com/")
    prompt = f"Тема модуля: {user_prompt['educational_module']}. Навыки, которые должен получить обучающийся: {list_skills}. Дополнительная информация: {user_prompt['additional_info']}"
    messages = [
        {"role": "system", "content": "Ты пишешь задания с развёрнутым ответом (ответ от одного слова до трёх предложений) на русском языке. Выводишь только json со структурой {tasks: [{text, skills: [], answer}]. text - текст вопроса, answer - ответ на вопрос. Количество заданий 1 штука. Дополнительнцю информацию в вопросе считай приоритетной, если она есть. "},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=1.2
            )
    result = json.loads(response.choices[0].message.content)
    task_materials: list[TaskMaterial] = []
    for task in result['tasks']:
        skills_str = ', '.join(task['skills'])
        material = TaskMaterial(
            text=task['text'],
            skills=skills_str,
            answer=task['answer']
        )
        task_materials.append(material)
    return task_materials


def yandex_search_first_link(query: str) -> str | None:
    time.sleep(1)
    query = "книга " + query
    url = "https://yandex.ru/search/xml"
    params = {
        "folderid": os.environ.get('YANDEX_FOLDER_ID'),
        "apikey": os.environ.get('YANDEX_API_KEY'),
        "l10n": "ru",
        "sortby": "rlv",
        "filter": "none",
        "maxpassages": "1",
        "groupby": "attr=d.mode=deep.groups-on-page=100.docs-in-group=1",
        "query": query,
        "page": 0,
        "lr": 213,
    }

    headers = {}

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        root = etree.fromstring(response.content)
        first_url = root.find('.//doc/url')
        if first_url is not None:
            first_url_str = first_url.text
            return first_url_str
        else:
            print("Нет результатов.")
            return None
    else:
        print("Ошибка запроса:", response.status_code)
        print(response.text)
        return None
