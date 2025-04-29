from sqlalchemy.orm import Session
from src.database import models
import pandas as pd
from openai import OpenAI
import json
import os
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from gensim.models import CoherenceModel
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def analyse_vacancy(db, id_profession):
    df = get_skills_by_profession(db, id_profession)
    topics_data = get_skill_topics(df)
    knowledge_areas = get_knowledge_areas_by_topics(topics_data)
    save_knowledge_areas_to_db(db, knowledge_areas, id_profession)

def save_knowledge_areas_to_db(db, knowledge_areas, id_profession):
    try:
        saved_count_skills = 0
        saved_count_areas = 0
        saved_count_relations = 0
        
        # Сначала сохраняем все навыки
        for area in knowledge_areas:
            for skill_name in area["topic_words"]:
                new_skill = models.Skill(
                    id_profession=int(id_profession),
                    name_skill=skill_name
                )
                db.add(new_skill)
                db.flush()  # Чтобы получить ID нового навыка
                saved_count_skills += 1

        # Затем сохраняем области знаний
        knowledge_area_ids = {}
        for area in knowledge_areas:
            new_knowledge_area = models.KnowledgeArea(
                id_profession=int(id_profession),
                name_knowledge_area=area["name"]
            )
            db.add(new_knowledge_area)
            db.flush()  # Чтобы получить ID новой области
            knowledge_area_ids[area["name"]] = new_knowledge_area.id_knowledge_area
            saved_count_areas += 1
        
        # Теперь сохраняем связи между навыками и областями знаний
        for area in knowledge_areas:
            knowledge_area_id = knowledge_area_ids[area["name"]]
            for skill_name in area["topic_words"]:
                # Находим ID навыка
                skill = db.query(models.Skill).filter_by(
                    id_profession=int(id_profession),
                    name_skill=skill_name
                ).first()
                
                if skill:
                    # Создаем связь
                    new_relation = models.SkillByKnowledgeArea(
                        id_skill=int(skill.id_skill),
                        id_knowledge_area=int(knowledge_area_id)
                    )
                    db.add(new_relation)
                    saved_count_relations += 1
        
        db.commit()
        print(f"Успешно сохранено {saved_count_skills} навыков")
        print(f"Успешно сохранено {saved_count_areas} областей")
        print(f"Успешно сохранено {saved_count_relations} связей между навыками и областями")
        return "Успешно"
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка при сохранении: {str(e)}")
        return str(e)
        

def get_skill_topics(df):
    all_phrases = []
    for skills_str in df['key_skills']:
        phrases = [phrase.strip() for phrase in skills_str.split(',')]
        all_phrases.extend(phrases)
    
    unique_processed_phrases = list(set(
        preprocess_phrase(phrase) for phrase in all_phrases
    ))

    df_unique_skills = pd.DataFrame({'skill': unique_processed_phrases})
    vectorizer = TfidfVectorizer(max_features=500)
    X = vectorizer.fit_transform(unique_processed_phrases)
    tfidf500 = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
    best_params, best_score = find_optimal_dbscan_params(unique_processed_phrases, X)

    print(f"Лучшие параметры: eps={best_params['eps']}, min_samples={best_params['min_samples']}")
    print(f"Лучший silhouette score: {best_score}")
    dbscan = DBSCAN(eps=best_params['eps'], min_samples=best_params['min_samples'])
    labels = dbscan.fit_predict(X)
    clasters_dbscan = dbscan.labels_
    clasters_dbscan = pd.DataFrame(clasters_dbscan, columns = ['klaster'])
    k = len(clasters_dbscan.value_counts())

    df_skills = pd.DataFrame({'skill': []})

    for i in range(k):
        words = df_unique_skills.skill[clasters_dbscan.klaster == i]  # Тексты кластера
        most_common_words = Counter(words).most_common(k)

        new_row = {'skill': " ".join([word for word, _ in most_common_words])}
        df_skills = pd.concat([df_skills, pd.DataFrame([new_row])], ignore_index=True)

        print(f"Кластер {i+1}:")
        print(" ".join([word for word, _ in most_common_words]))  # Вывод слов

    best_params, best_coherence = find_optimal_lda_params(df_skills, clasters_dbscan)

    words = list(df_skills.skill[clasters_dbscan.klaster > 0].apply(word_tokenize))
    dictionary = Dictionary(words)
    corpus = [dictionary.doc2bow(doc) for doc in words]

    # Обучение LDA модели
    num_topics = best_params['num_topics']
    alpha = best_params['alpha']
    eta = best_params['eta']

    lda_model = LdaModel(corpus, num_topics=num_topics, alpha = alpha, eta = eta, id2word=dictionary, passes=10)
    
    topics_data = []
    for idx, topic in lda_model.print_topics(-1):
        # Разделяем строку на слова и веса
        topic_words = [word.split('*')[1].strip('"') for word in topic.split(' + ')]
        print(f"Topic {idx}: {', '.join(topic_words)}")
        topics_data.append({
            "id": idx,
            "topic_words": topic_words
        })
    return topics_data

def get_knowledge_areas_by_topics(topics_data):
    client = OpenAI(api_key=os.environ.get('DEEPSEEK_TOKEN'), base_url="https://api.deepseek.com")

    # Формируем JSON-промпт (пустая строка + данные)
    prompt = "Дай каждому топику название по структуре id name (название, которое ты дал) topic_words (массив слов) результат выведи только в json (без дополнительного текста):"  
    messages = [
        {"role": "system", "content": "Ты — помощник, который даёт темам названия на русском."},
        {"role": "user", "content": prompt + ' ' + json.dumps(topics_data, ensure_ascii=False)}
    ]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3
        )
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        raise Exception(f"API request failed: {e}")


def find_optimal_lda_params(df_skills, clasters_dbscan):
    words = list(df_skills.skill[clasters_dbscan.klaster > 0].apply(word_tokenize))
    dictionary = Dictionary(words)
    corpus = [dictionary.doc2bow(doc) for doc in words]
    # Параметры для поиска
    num_topics_list = range(6, 10)
    alpha_list = ['symmetric','auto']
    eta_list = ['symmetric','auto']

    best_coherence = -1
    best_params = {}

    for num_topics in num_topics_list:
        for alpha in alpha_list:
            for eta in eta_list:
                lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, alpha=alpha, eta=eta, passes=10)
                coherence_model = CoherenceModel(model=lda_model, texts=words, dictionary=dictionary, coherence='c_v')
                coherence_score = coherence_model.get_coherence()

                if coherence_score > best_coherence:
                    best_coherence = coherence_score
                    best_params = {'num_topics': num_topics, 'alpha': alpha, 'eta': eta}

    print(f'Best Coherence Score: {best_coherence}')
    print(f'Best Parameters: {best_params}')
    return best_params, best_coherence

def find_optimal_dbscan_params(phrases, X):
    min_samples_range = range(2, 5)  
    eps_range = np.linspace(0.1, 1.0, 10) 
    best_score = -1
    best_params = {'eps': None, 'min_samples': None}
    
    # Перебор параметров
    for min_samples in min_samples_range:
        for eps in eps_range:
            dbscan = DBSCAN(eps=eps, min_samples=min_samples)
            labels = dbscan.fit_predict(X)
            
            # Пропускаем случаи, когда все точки шум или только один кластер
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            if n_clusters < 2 or n_clusters > len(phrases) // 2:
                continue
                
            # Оценка качества кластеризации (только если есть кластеры)
            try:
                score = silhouette_score(X, labels)
                if score > best_score:
                    best_score = score
                    best_params['eps'] = eps
                    best_params['min_samples'] = min_samples
            except:
                continue
                
    return best_params, best_score


def preprocess_phrase(phrase: str) -> str:
    stop_words = set(stopwords.words('russian'))
    lemmatizer = WordNetLemmatizer()
    
    tokens = list(filter(str.isalpha, word_tokenize(phrase.lower())))
    
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    
    tokens = [word for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)


def get_skills_by_profession(db: Session, id_profession: int) -> pd.DataFrame:
    try:
        vacancies = db.query(models.Vacancy).filter(models.Vacancy.id_profession == id_profession).all()
        
        if not vacancies:
            print(f"Для профессии ID {id_profession} вакансии не найдены")
            return pd.DataFrame(columns=['key_skills'])
        
        data = [
            {
                'key_skills': vac.key_skills
            }
            for vac in vacancies
        ]

        df = pd.DataFrame(data)
        
        return df
    
    except Exception as e:
        print(f"Ошибка при получении данных: {str(e)}")
        return pd.DataFrame()