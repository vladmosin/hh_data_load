import json
import os
from collections import Counter
import pandas as pd


def load_all_vacancies(folder):
    vacancies = []
    for file_name in os.listdir(folder):
        with open(f'{folder}/{file_name}', 'r') as f:
            vacancy = json.load(f)

        vacancies.append(vacancy)

    return vacancies


def analyze_key_skills(vacancies):
    skills = []
    for vacancy in vacancies:
        for key_skill in vacancy['key_skills']:
            skills.append(key_skill['name'])

    return Counter(skills)


if __name__ == '__main__':
    vacancy_type_id = 2.164
    all_vacancies = load_all_vacancies(f'data/vacancies/{vacancy_type_id}')
    specializations = pd.read_csv('data/specializations.csv')

    vacancy_type_name = specializations[specializations.id == vacancy_type_id].iloc[0]['name']

    print(f'Vacancy: {vacancy_type_name}')
    for name, amount in analyze_key_skills(all_vacancies).most_common():
        print(f'{name:40}: {amount}')
