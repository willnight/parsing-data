# Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные данные в БД

from lxml import html
from pprint import pprint
import requests
from datetime import datetime, date, timedelta
import pymongo

translated_month = {'января': 'Jan',
                    'февраля': 'Feb',
                    'марта': 'Mar',
                    'апреля': 'Apr',
                    'мая': 'May',
                    'июня': 'Jun',
                    'июля': 'Jul',
                    'августа': 'Aug',
                    'сентября': 'Sep',
                    'октября': 'Oct',
                    'ноября': 'Nov',
                    'декабря': 'Dec'}


def parse_date(text, text_format):
    words = text.split()
    for i, word in enumerate(words):
        if translated_month.get(word) is not None:
            words[i] = translated_month.get(word)
    text = ' '.join(words)
    datetime_object = datetime.strptime(text.strip(), text_format)
    return datetime_object


def parse_yandex_date(text):
    res = ''
    words = text.split()
    today = date.today()
    yesterday = today - timedelta(days=1)

    if words.__contains__('вчера'):
        news_time = datetime.strptime(words[-1], '%H:%M').time()
        res = datetime.combine(yesterday, news_time)
    elif words.__contains__('в'):
        date_string = f'{words[0]} {words[1]} {today.year} {words[-1]}'
        res = datetime.strptime(date_string, '%d %b %Y %H:%M')
    else:
        news_time = datetime.strptime(words[0], '%H:%M').time()
        res = datetime.combine(today, news_time)
    return res


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
lenta_url = 'https://lenta.ru'
mail_url = 'https://news.mail.ru'
yandex_url = 'https://yandex.ru/news'
news_list = []

client = pymongo.MongoClient('localhost', 27017)
db = client['news_db']
news_collection = db['news']


def parse_news(source):
    response = requests.get(source)
    dom = html.fromstring(response.text)

    if source == lenta_url:
        items = dom.xpath("//section[contains(@class,'b-top7-for-main')]//a/time")
        for item in items:
            news = {}
            news = {'name': item.xpath("../text()")[0].replace(u'\xa0', ' '),
                    'link': f'{lenta_url}{item.xpath("../@href")[0]}',
                    'source': 'Lenta ru',
                    'date': item.xpath("../time/@datetime")[0].strip(),
                    'datetime': parse_date(item.xpath("../time/@datetime")[0], u'%H:%M, %d %b %Y')}
            news_list.append(news)

    elif source == mail_url:
        items = dom.xpath("//div[contains(@class,'daynews__item')]")
        for item in items:
            news = {}
            news['name'] = item.xpath(".//span[contains(@class, 'photo__title')]/text()")[0].replace(u'\xa0', ' ')
            link = f'{item.xpath("./a/@href")[0]}'
            news['link'] = link

            response_item = requests.get(link)
            dom_item = html.fromstring(response_item.text)

            news['source'] = dom_item.xpath("//span[@class='breadcrumbs__item']//span[contains(@class,'link__text')]/text()")[0]
            date_string = dom_item.xpath("//span[@class='breadcrumbs__item']//span[contains(@class,'note__text')]/@datetime")[0]
            news['date'] = date_string[:len(date_string) - 6]
            news['datetime'] = parse_date(date_string[:len(date_string) - 6], '%Y-%m-%dT%H:%M:%S')

            news_list.append(news)

    elif source == yandex_url:
        items = dom.xpath("//div[contains(@class,'mg-grid__row_gap_8')][3]//article[contains(@class,'mg-card')]")
        for item in items:
            news = {'name': item.xpath(".//h2[@class='mg-card__title']/text()")[0].replace(u'\xa0', ' '),
                    'link': item.xpath(".//a[@class='mg-card__link']/@href")[0],
                    'source': item.xpath(".//a[@class='mg-card__source-link']/text()")[0],
                    'date': item.xpath(".//span[@class='mg-card-source__time']/text()")[0],
                    'datetime': parse_yandex_date(item.xpath(".//span[@class='mg-card-source__time']/text()")[0])}

            news_list.append(news)


for el in news_list:
    if news_collection.find({'name': el.get('name')}).count() < 1:
        news_collection.insert_one(el)


parse_news(lenta_url)
parse_news(mail_url)
parse_news(yandex_url)
# pprint(news_list)

for i in news_collection.find({}):
    pprint(i)

pprint(news_collection.count_documents({}))
