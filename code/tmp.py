import os
from pathlib import Path
import pandas as pd


def copy_data(from_path='tmp_data', to_path='data/vacancies'):
    for folder in os.listdir(from_path):
        for vacancy_folder in os.listdir(f'{from_path}/{folder}/vacancies'):
            folder_to_copy = f'{from_path}/{folder}/vacancies/{vacancy_folder}'
            if not os.path.exists(f'{to_path}/{vacancy_folder}'):
                os.system(f'cp -r {folder_to_copy} {to_path}')
            else:
                for file_name in os.listdir(folder_to_copy):
                    if not os.path.exists(f'{to_path}/{vacancy_folder}/{file_name}'):
                        os.system(f'cp {folder_to_copy}/{file_name} {to_path}/{vacancy_folder}')


def save_not_found_specializations(path_to_specializations='data/vacancy_ids', new_path='data/new_vacancy_ids'):
    loaded_vacancies = os.listdir('data/vacancies')
    Path(new_path).mkdir(exist_ok=True, parents=True)

    for vacancy in os.listdir(path_to_specializations):
        vacancy_id = vacancy.split('_')[0]
        if vacancy_id not in loaded_vacancies:
            os.system(f'cp "{path_to_specializations}/{vacancy}" {new_path}')
            #print(f'cp "{path_to_specializations}/{vacancy}" {new_path}')


def compute_total_vacancies(path='data/vacancy_ids'):
    all_ids = []
    for file_name in os.listdir(path):
        ids = pd.read_csv(f'{path}/{file_name}').id
        all_ids.extend(ids)

    return len(set(all_ids))


if __name__ == '__main__':
    #copy_data()
    #save_not_found_specializations()
    print(compute_total_vacancies())
