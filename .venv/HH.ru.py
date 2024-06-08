"""
Нужно выбрать те вакансии, у которых в описании есть ключевые слова "Django" и "Flask".
Записать в json информацию о каждой вакансии - ссылка, вилка зп, название компании, город.
"""


import bs4
from pprint import pprint as pp
import requests
from fake_headers import Headers
from time import sleep
import json

def get_headers():
    return Headers(os='win', browser='chrome').generate()

# print(get_headers())

response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=get_headers())

main_html_data = response.text

main_soup = bs4.BeautifulSoup(main_html_data, features='lxml')

tag_div_vacancy_list = main_soup.find_all('span', class_='serp-item__title-link-wrapper')

parsed_data = []

for link in tag_div_vacancy_list:
    a_tag = link.find('a')
    absolute_link = a_tag['href']

    vacancy_response = requests.get(absolute_link, headers=get_headers())
    vacancy_response_html_data = vacancy_response.text
    vacancy_soup = bs4.BeautifulSoup(vacancy_response_html_data, features='lxml')

    div_tag_title = vacancy_soup.find('h1', class_='bloko-header-section-1')
    title = div_tag_title.text

    tag_salary = vacancy_soup.find('span', class_='magritte-text___pbpft_3-0-4 magritte-text_style-primary___AQ7MW_3-0-4 magritte-text_typography-label-1-regular___pi3R-_3-0-4')
    salary = tag_salary.text.replace('\xa0', ' ')

    tag_company = vacancy_soup.find('div', class_='vacancy-company-redesigned')
    company_name = tag_company.find('span').text.replace("ООО",'')
    formated_company = company_name.replace('\xa0', '')

    tag_city = vacancy_soup.find(attrs={'data-qa': 'vacancy-view-location'})
    if tag_city is None:
        city_name = vacancy_soup.find(attrs={'data-qa': 'vacancy-view-raw-address'}).text
    else: city_name = tag_city.text

    tag_skills = vacancy_soup.find_all('div', class_='magritte-tag__label___YHV-o_2-0-6')
    skills = []
    for skill in tag_skills:
        skills.append(skill.text)


    parsed_data.append({
        'title': title,
        'link': absolute_link,
        'salary': salary,
        'company': formated_company,
        'city': city_name,
        'skills': skills
    })

filtered_vacancies = []
for vacancy in parsed_data:
    skills = vacancy.get('skills', [])
    if any(skill in skills for skill in ['Django', 'Flask']):
        filtered_vacancies.append(vacancy)

with open('filtered_vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_vacancies, f, ensure_ascii=False, indent=4)

