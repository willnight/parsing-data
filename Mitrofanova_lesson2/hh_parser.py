# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы)
# с сайтов Superjob и HH.
# Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
# Получившийся список должен содержать в себе минимум:
# Наименование вакансии.
# Предлагаемую зарплату (отдельно минимальную и максимальную).
# Ссылку на саму вакансию.
# Сайт, откуда собрана вакансия.
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.
# Можно выполнить по желанию один любой вариант или оба при желании и возможности.


import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from IPython.core.display import display, HTML


def get_vacancy_money_range(text):
    if text is None:
        return None, None, None
    words = text.split(' ')
    if 'от' in words:
        return int(words[1].replace(u'\u202f', '')), None, words[2]
    elif '–' in words:
        return int(words[0].replace(u'\u202f', '')), int(words[2].replace(u'\u202f', '')), words[3]
    else:
        return None, None, None


vacancy = input("Введите название вакансии для поиска: ").replace(' ', '+')
page_num = 0
btn_next_page = ''
serials = []

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 OPR/76.0.4017.107'}


while btn_next_page is not None:
    url = f'https://spb.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text={vacancy}&showClusters=true&page={page_num}'
    print(f"Now requesting to page {page_num}...")
    response = requests.get(url, headers=headers)
    dom = bs(response.text, 'html.parser')
    btn_next_page = dom.find('a', attrs={'data-qa': 'pager-next'})

    serials_list = dom.find_all('div', attrs={'class': 'vacancy-serp-item'})
    serials.extend(serials_list)
    page_num += 1

data_grid = {}
vacancy_name_list = []
vacancy_href_list = []
vacancy_employer_list = []
vacancy_city_list = []
vacancy_money_min_list = []
vacancy_money_max_list = []
vacancy_money_curr_list = []
vacancy_source_list = []

for serial in serials:
    # print(serial)
    vacancy_name = serial.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).getText()
    vacancy_href = serial.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href'].split('?')[0]
    vacancy_employer = serial.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).getText()
    vacancy_city = serial.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]
    sp_vacancy_money = serial.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})

    if sp_vacancy_money is not None:
        vacancy_money = sp_vacancy_money.getText()
    else:
        vacancy_money = None

    money = get_vacancy_money_range(vacancy_money)

    vacancy_name_list.append(vacancy_name)
    vacancy_href_list.append(f'<a target="_blank" href="{vacancy_href}">{vacancy_href}</a>')
    vacancy_employer_list.append(vacancy_employer)
    vacancy_city_list.append(vacancy_city)
    # возвращаю в таблицу '' вместо None для удобства отображения
    vacancy_money_min_list.append('' if money[0] is None else money[0])
    vacancy_money_max_list.append('' if money[1] is None else money[1])
    vacancy_money_curr_list.append('' if money[2] is None else money[2])
    vacancy_source_list.append('hh.ru')


data_grid['Вакансия'] = vacancy_name_list
data_grid['Город'] = vacancy_city_list
data_grid['Компания'] = vacancy_employer_list
data_grid['ЗП от'] = vacancy_money_min_list
data_grid['ЗП до'] = vacancy_money_max_list
data_grid['валюта'] = vacancy_money_curr_list
data_grid['ссылка'] = vacancy_href_list
data_grid['источник'] = vacancy_source_list

df = pd.DataFrame(data=data_grid)
pd.set_option('display.max_rows', df.shape[0]+1)

display(HTML(df.to_html(escape=False)))

with open(f'vacancy_parsed_data.html', 'w') as f:
    f.write(HTML(df.to_html(escape=False)).data)
