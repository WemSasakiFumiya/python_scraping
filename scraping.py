import requests
from bs4 import BeautifulSoup


def get_scraping_data():
    response = requests.get('https://member.digskill.net/trial')
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').text
    return title


print(get_scraping_data())
