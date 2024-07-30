import requests
from tqdm import tqdm
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup

SOFTWARE_NAMES = [SoftwareName.CHROME.value]
OPERATING_SYSTEMS = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
USER_AGENT = UserAgent(software_names=SOFTWARE_NAMES, operating_systems=OPERATING_SYSTEMS, limit=100)

def get_pages_amount(page):
    num = page.find("div", {"data-qa": "pager-block"})

    if not num:
        return 1

    num = num.findAll("a", {"class": "bloko-button"})

    if not num:
        return 1

    return int(num[-2].getText())


def parse_resume_ids(page):
    hashes = []

    if page is not None:
        hashes = page.findAll("div", {"data-qa": "resume-serp__resume"})
        hashes = [item.find("a")["href"][8:46] for item in hashes]

    return hashes


def get_page(vacancy, page_number):
    response = requests.get(
        f'https://hh.ru/search/resume',
        headers={'User-Agent': USER_AGENT.get_random_user_agent()},
        params={
            'text': vacancy,
            'order_by': 'relevance',
            'logic': 'normal',
            'pos': 'full_text',
            'exp_period': 'all_time',
            'page': page_number
        }
    )

    return BeautifulSoup(response.content)


def get_resume_ids(vacancy, amount):
    page = get_page(vacancy, page_number=0)
    pages_amount = get_pages_amount(page)

    resume_ids = []
    for page_number in tqdm(range(pages_amount)):
        page = get_page(vacancy, page_number=page_number)
        resume_ids.extend(parse_resume_ids(page))

        if len(resume_ids) > amount:
            break

    return resume_ids[:amount]


def get_skills(page):
    page = page.find("div", {"data-qa": "skills-table", "class": "resume-block"})

    page_skill_set = []
    if page is not None:
        page_skill_set = page.findAll("div", {"class": "bloko-tag bloko-tag_inline",
                                              "data-qa": "bloko-tag bloko-tag_inline"})
        page_skill_set = [skill.getText() for skill in page_skill_set]

    return page_skill_set


def get_skills_from_resume(resume_id):
    response = requests.get(
        f'https://hh.ru/resume/{resume_id}',
        headers={'User-Agent': USER_AGENT.get_random_user_agent()}
    )

    page = BeautifulSoup(response.content)
    return get_skills(page)


def load_skills_by_resume_ids(resume_ids):
    return {
        resume_id: get_skills_from_resume(resume_id) for resume_id in tqdm(resume_ids)
    }


def load_skills_by_vacancy(vacancy, amount=1000000):
    resume_ids = get_resume_ids(vacancy, amount)
    return list(load_skills_by_resume_ids(resume_ids).values())


if __name__ == '__main__':
    load_skills_by_vacancy('Python developer', 10)
