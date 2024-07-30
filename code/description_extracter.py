import json
import os

PHRASES = ['требования', 'наши ожидания']
POSSIBLE_TAGS = [
    ['<li>', '</li>'],
    ['<p>', '</p>']
]


def to_first_last_letter(requirement):
    start_index = 0
    for i in range(len(requirement)):
        if requirement[i].isalpha():
            start_index = i
            break

    end_index = len(requirement) - 1
    while end_index > start_index:
        if requirement[end_index].isalpha():
            break
        else:
            end_index -= 1

    return requirement[start_index:end_index + 1]


def parse_between_tags(requirements):
    all_requirements_best = []
    for start_tag, end_tag in POSSIBLE_TAGS:
        all_requirements = []
        for part in requirements.split(start_tag):
            between_tags = part.split(end_tag)
            if len(between_tags) > 1:
                all_requirements.append(to_first_last_letter(between_tags[0]))

        if len(all_requirements_best) < len(all_requirements):
            all_requirements_best = all_requirements

    return all_requirements_best


def extract_from_description(path='data/vacancies/1/35618755.json'):
    with open(path, 'r') as f:
        config = json.load(f)

    description = config['description']

    requirements = None
    requirements_found = False

    for part in description.lower().split('<strong>'):
        for phrase in PHRASES:
            if part.startswith(phrase):
                requirements = part
                requirements_found = True
                break

        if requirements_found:
            break

    if requirements is not None:
        return parse_between_tags(requirements)
    else:
        print(description)
        return []


def extract_all_from_folder(folder='data/vacancies/1'):
    all_requirements = []
    for file_name in os.listdir(folder)[:10]:
        requirements = extract_from_description(f'{folder}/{file_name}')
        all_requirements.append(requirements)

    return all_requirements


if __name__ == '__main__':
    print(extract_from_description())
    #extract_all_from_folder()
