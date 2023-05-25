import requests
from bs4 import BeautifulSoup


def get_scraping_data(prefecture):
    response = requests.get('https://tabelog.com/' + prefecture + '/rstLst')
    soup = BeautifulSoup(response.content, 'html.parser')
    rst_name_targets = soup.find_all('a', class_='list-rst__rst-name-target')
    names = [name_target.text for name_target in rst_name_targets]
    return names


print(get_scraping_data('kanagawa'))
