import os.path

import requests
import pandas as pd
from tqdm import tqdm
from time import sleep
from pathlib import Path
import json

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

SOFTWARE_NAMES = [SoftwareName.CHROME.value]
OPERATING_SYSTEMS = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
USER_AGENT = UserAgent(software_names=SOFTWARE_NAMES, operating_systems=OPERATING_SYSTEMS, limit=100)


def make_request_with_ban_detection(url, headers, params={}, current_sleep=1):
    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    if response.ok:
        return response
    else:
        error_type = response.json()['errors'][0]['type']
        if error_type == 'not_found':
            return None
        elif error_type == 'captcha_required':
            if current_sleep > 60:
                raise Exception('Too long sleep')
            sleep(current_sleep)
            return make_request_with_ban_detection(url, headers, params, current_sleep=current_sleep * 2)
        else:
            print(response.json())
            raise Exception(f'Unknown error type: {error_type}')


def flatten_areas(areas, depth=0):
    if len(areas) == 0:
        return [], [], [], []

    all_ids = []
    all_parents = []
    all_names = []
    all_depths = []
    for area in areas:
        ids, parents, names, depths = flatten_areas(area['areas'], depth + 1)

        all_ids.extend(ids)
        all_parents.extend(parents)
        all_names.extend(names)
        all_depths.extend(depths)

        all_ids.append(area['id'])
        all_parents.append(area['parent_id'])
        all_names.append(area['name'])
        all_depths.append(depth)

    return all_ids, all_parents, all_names, all_depths


def get_all_areas():
    response = make_request_with_ban_detection(
        f'https://api.hh.ru/areas',
        headers={'User-Agent': USER_AGENT.get_random_user_agent()}
    )

    ids, parents, names, depths = flatten_areas(response.json())

    return pd.DataFrame.from_dict({'id': ids, 'parent': parents, 'name': names, 'depth': depths})


def flatten_specializations(specializations):
    if len(specializations) == 0:
        return [], []

    all_ids = []
    all_names = []

    for specialization in specializations:
        if 'industries' in specialization:
            ids, names = flatten_specializations(specialization['industries'])

            all_ids.extend(ids)
            all_names.extend(names)

        all_ids.append(specialization['id'])
        all_names.append(specialization['name'])

    return all_ids, all_names


def get_all_specializations():
    response = make_request_with_ban_detection(
        f'https://api.hh.ru/industries',
        headers={'User-Agent': USER_AGENT.get_random_user_agent()}
    )

    ids, names = flatten_specializations(response.json())

    return pd.DataFrame.from_dict({'id': ids, 'name': names})


def load_vacancies(specialization, area):
    response = make_request_with_ban_detection(
        f'https://api.hh.ru/vacancies?industry={specialization}&area={area}',
        headers={'User-Agent': USER_AGENT.get_random_user_agent()},
        params={
            'per_page': 100,
            'page': 0
        }
    )

    response = response.json()
    try:
        pages = response['pages']
    except:
        print(response)
        sleep(100)
        return []

    vacancies = []

    for page in range(pages):
        response = make_request_with_ban_detection(
            f'https://api.hh.ru/vacancies?industry={specialization}&area={area}',
            headers={'User-Agent': USER_AGENT.get_random_user_agent()},
            params={
                'per_page': 100,
                'page': page
            }
        )

        response = response.json()
        if 'items' in response:
            for item in response['items']:
                vacancies.append(item['id'])

    return vacancies


def load_vacancy_by_id(folder, vacancy_id):
    file_path = f'{folder}/{vacancy_id}.json'
    if os.path.exists(file_path):
        return

    Path(folder).mkdir(parents=True, exist_ok=True)

    response = make_request_with_ban_detection(
        f'https://api.hh.ru/vacancies/{vacancy_id}',
        headers={'User-Agent': USER_AGENT.get_random_user_agent()}
    )

    if response is not None:
        with open(file_path, 'w') as f:
            json.dump(response.json(), f, indent=4)


def load_vacancies_from_file(path):
    vacancy_group = path.split('/')[-1].split('_')[0]
    for vacancy_id in tqdm(pd.read_csv(path).id):
        load_vacancy_by_id(f'data/vacancies/{vacancy_group}', vacancy_id)


def load_all_vacancies(path):
    for file_name in os.listdir(path):
        load_vacancies_from_file(f'{path}/{file_name}')


if __name__ == '__main__':
    specializations = get_all_specializations()
    specializations.to_csv('data/industries.csv', index=False)
    areas = get_all_areas()
    areas = areas[areas.id == '113']

    all_vacancies = []
    for specialization in tqdm(specializations.id):
        specialization_name = specializations[specializations.id == specialization].iloc[0]['name']
        filename = f'{specialization}_{specialization_name}.csv'.replace('/', '%')

        if not os.path.exists(f'data/vacancy_ids_1/{filename}'):
            for area in areas.id:
                vacancies = load_vacancies(specialization, area)
                all_vacancies.extend(vacancies)

            vacancies = pd.DataFrame.from_dict({'id': list(set(all_vacancies))})
            vacancies.to_csv(f'data/vacancy_ids_1/{filename}', index=False)

    # load_vacancy_by_id('/Users/vlad/Education/Leya/RecSys/data/vacancies', 104474007)
    # load_all_vacancies('/Users/vlad/Education/Leya/RecSys/data/vacancy_ids')

    # load_all_vacancies('/Users/vlad/Education/Leya/RecSys/data/vacancy_ids')
