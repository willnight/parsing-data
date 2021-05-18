# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# записывающую собранные вакансии в созданную БД.
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

import requests
from bs4 import BeautifulSoup as bs
import pymongo
from pprint import pprint
import hashlib
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

superjob_name = 'superjob.ru'
hh_name = 'hh.ru'

# vacancy_search_name = input("Введите название вакансии для поиска: ").replace(' ', '+')
vacancy_search_name = 'python'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.107'}

# для быстрого тестирования стоит 10, если нужны все данные можно вернуть на 1
search_pages_step = 10

client = pymongo.MongoClient('localhost', 27017)
db = client['vacancy_db']
superjob_collection = db['superjob_collection']
hh_collection = db['hh_collection']

# superjob_collection.delete_many({})
# hh_collection.delete_many({})


def get_vacancy_money_range(text, source):
    if text is None:
        return None, None, None
    text = text.replace(u'\xa0', u'')
    if source == superjob_name:
        text = text.replace('от', 'от ')
        text = text.replace('до', 'до ')
        text = text.replace('—', ' — ')
        text = text.replace('руб.', ' руб.')
    words = text.split(' ')
    if 'от' in words:
        return int(words[1].replace(u'\u202f', '')), None, words[2]
    elif 'до' in words and 'говорённости' not in words:
        return None, int(words[1].replace(u'\u202f', '')), words[2]
    elif '–' in words or '—' in words:
        return int(words[0].replace(u'\u202f', '')), int(words[2].replace(u'\u202f', '')), words[3]
    else:
        return None, None, None


def parse_data(source):
    page_num = 0
    btn_next_page = ''
    vacancy_list = []
    vacancy_elements = []
    result_data_grid = []

    while btn_next_page is not None:
        if source == hh_name:
            url = f'https://spb.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text={vacancy_search_name}&showClusters=true&page={page_num}'
            print(f"Now requesting to {source} page {page_num}...")
            response = requests.get(url, headers=headers)
            dom = bs(response.text, 'html.parser')
            btn_next_page = dom.find('a', attrs={'data-qa': 'pager-next'})
            vacancy_elements = dom.find_all('div', attrs={'class': 'vacancy-serp-item'})
        elif source == superjob_name:
            url = f'https://spb.superjob.ru/vacancy/search/?keywords={vacancy_search_name}&page={page_num}'
            print(f"Now requesting to {source} page {page_num}...")
            response = requests.get(url, headers=headers)
            dom = bs(response.text, 'html.parser')
            btn_next_page = dom.find('a', attrs={'class': 'f-test-button-dalshe'})
            vacancy_elements = dom.find_all('div', attrs={'class': 'f-test-vacancy-item'})

        vacancy_list.extend(vacancy_elements)
        page_num += search_pages_step

    for vacancy in vacancy_list:
        if source == hh_name:
            vacancy_name = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).getText()
            vacancy_url = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href'].split('?')[0]
            vacancy_employer = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).getText()
            vacancy_city = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]
            sp_vacancy_money = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if sp_vacancy_money is not None:
                vacancy_money = sp_vacancy_money.getText()
            else:
                vacancy_money = None
            money = get_vacancy_money_range(vacancy_money, hh_name)

        elif source == superjob_name:
            vacancy_name = \
                vacancy.find('span', attrs={'class': 'f-test-text-company-item-salary'}).previous_sibling.find('a').getText()
            vacancy_href = vacancy.find('span', attrs={'class': 'f-test-text-company-item-salary'}).previous_sibling.find('a')['href']
            vacancy_url = f'https://spb.superjob.ru/{vacancy_href}'
            vacancy_employer = vacancy.find('span', attrs={'class': 'f-test-text-vacancy-item-company-name'}).find('a').getText()

            cities = vacancy.find('span', attrs={'class': 'f-test-text-company-item-location'}).find_all('span')
            if len(cities) > 3:
                vacancy_city = cities[3].getText().split(',')[0]
            else:
                vacancy_city = cities[len(cities) - 1].getText().split(',')[0]

            sp_vacancy_money = vacancy.find('span', attrs={'class': 'f-test-text-company-item-salary'}).find('span')
            if sp_vacancy_money is not None:
                vacancy_money = sp_vacancy_money.getText()
            else:
                vacancy_money = None
            money = get_vacancy_money_range(vacancy_money, superjob_name)

        vacancy_hash_string = f'{vacancy_name}{vacancy_employer}{vacancy_city}{money}{source}'
        vacancy_hash = hashlib.sha224(vacancy_hash_string.encode('utf-8')).hexdigest()

        data = {'Вакансия': vacancy_name,
                'Город': vacancy_city,
                'Компания': vacancy_employer,
                'ЗП от': '' if money[0] is None else money[0],
                'ЗП до': '' if money[1] is None else money[1],
                'валюта': '' if money[2] is None else money[2],
                'ссылка': f'<a target="_blank" href="{vacancy_url}">{vacancy_url}</a>',
                'источник': source,
                'hash': vacancy_hash}

        if source == hh_name:
            if hh_collection.find({'hash': vacancy_hash}).count() < 1:
                hh_collection.insert_one(data)
        elif source == superjob_name:
            if superjob_collection.find({'hash': vacancy_hash}).count() < 1:
                superjob_collection.insert_one(data)

        result_data_grid.append(data)
    return result_data_grid


def get_vacancy_from_salary(collection, value):
    return collection.find({'$or': [{'ЗП от': {'$gt': value}}, {'ЗП до': {'$gt': value}}]})


parse_data(hh_name)
parse_data(superjob_name)

print(f'Размер {hh_collection.name}: {hh_collection.count_documents({})}')
print(f'Размер {superjob_collection.name}: {superjob_collection.count_documents({})}')

salary = int(input("Введите сумму ЗП для фильтрации (отобразится все, что больше суммы): "))
for i in get_vacancy_from_salary(hh_collection, salary):
    pprint(i)

# для первого задания:
# superjob_collection = db['superjob_collection']
# hh_collection = db['hh_collection']
#
# hh_collection.insert_many(parse_data(hh_name))
# superjob_collection.insert_many(parse_data(superjob_name))
#
# for i in hh_collection.find({}):
#     pprint(i)
