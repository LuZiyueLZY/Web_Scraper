import os
import requests as rq
from bs4 import BeautifulSoup
from http import HTTPStatus
import re


headers = {'Accept-Language': 'en-UK,en;q=0.5'}
base_url = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020&page='
num_page = input('Enter the page number: ')
article_type = input('Enter the article type: ')

for page in range(1, int(num_page) + 1):
    url = f'{base_url}{page}'
    r = rq.get(url, headers=headers)
    r.raise_for_status()

    try:
        if r.status_code == HTTPStatus.OK:
            soup = BeautifulSoup(r.content, 'html.parser')
            articles = soup.find_all('article')
            os.makedirs(f'Page_{page}', exist_ok=True)
            titles = []
            sub_links = []
            for article in articles:
                span = article.find('span', {'data-test': 'article.type'})
                if span and span.get_text(strip=True).lower() == article_type.lower():
                    title_tag = article.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    link_tag = article.find('a', {'data-track-action': 'view article'})
                    if link_tag:
                        sub_links.append(link_tag.get('href'))
            links = [f'https://www.nature.com{sub_link}' for sub_link in sub_links]
            for link in links:
                article_r = rq.get(link, headers=headers)
                article_r.raise_for_status()
                if article_r.status_code == HTTPStatus.OK:
                    article_soup = BeautifulSoup(article_r.content, 'html.parser')
                    article_title = article_soup.title.string.strip() if article_soup.title else 'No title found'
                    article_title = re.sub(r'[^\w\s]', '', article_title)
                    article_title = article_title.replace(' ', '_')
                    body = article_soup.find('p', {'class': 'article__teaser'}).get_text(strip=True) if article_soup.find('p', {'class': 'article__teaser'}) else 'No body found'
                    with open(f'Page_{page}/{article_title}.txt', 'w', encoding='utf-8') as file:
                        file.write(body)
                    print(f'File {article_title}.txt has been created.')
    except rq.exceptions.HTTPError as e:
        print(f'The URL returned {e.response.status_code}!')
