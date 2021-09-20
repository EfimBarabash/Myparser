import json

import requests
from bs4 import BeautifulSoup
import csv

url = 'https://calorizator.ru/product'
res = requests.get(url)

soup = BeautifulSoup(res.text, 'lxml')
all_group = soup.find_all('ul', class_='product')

#Сбор всех категорий
all_category = {}
for item in all_group[:-1]:
    all_link = item.find_all('a')
    for link in all_link:
        link_name = link.text
        link_url = 'https://calorizator.ru/' + link.get('href')
        all_category[link_name] = link_url


headers_table = None

for name, link in all_category.items():
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'lxml')

    if headers_table is None:
        headers_table = [text.replace(', ', '_') for text in soup.find(id='main-content').find('thead').stripped_strings]

    #Извлечение данных из таблицы
    content = []
    for tr in soup.find(id='main-content').find('tbody').find_all('tr'):
        all_td = tr.find_all('td')
        title = all_td[1].text.strip()
        proteins = all_td[2].text.strip()
        fats = all_td[3].text.strip()
        carbohydrates = all_td[4].text.strip()
        calories = all_td[5].text.strip()
        content.append([title, proteins, fats, carbohydrates, calories])

    #Проверяем есть ли пагинатор
    paginator = soup.find('ul', class_='pager')
    if paginator is not None:
        pages = paginator.find_all('li', class_='pager-item')
        #Обход всех страниц текущей категории товара
        for number_page in range(1, len(pages)+1):
            res = requests.get(link, params={'page': number_page})
            soup = BeautifulSoup(res.text, 'lxml')
            # Извлечение данных из таблицы
            for tr in soup.find(id='main-content').find('tbody').find_all('tr'):
                all_td = tr.find_all('td')
                title = all_td[1].text.strip()
                proteins = all_td[2].text.strip()
                fats = all_td[3].text.strip()
                carbohydrates = all_td[4].text.strip()
                calories = all_td[5].text.strip()
                content.append([title, proteins, fats, carbohydrates, calories])

    #Запись csv файлов
    with open(f'documet/{name}.csv', 'w', encoding='utf-8') as file_csv:
        writer = csv.writer(file_csv, delimiter=',')
        writer.writerow(headers_table)
        writer.writerows(content)


    product_info = []
    for product in content:
        product_info.append({
            'title': product[0],
            'proteins': product[1],
            'fats': product[2],
            'carbohydrates': product[3],
            'calories': product[4]
        })

    # Запись json файлов
    with open(f'documet/{name}.json', 'w', encoding='utf-8') as file_json:
        json.dump(product_info, file_json, indent=4, ensure_ascii=False)

