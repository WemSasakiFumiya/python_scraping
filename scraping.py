import requests
from bs4 import BeautifulSoup
from time import sleep


def get_scraping_data(prefecture, page_num):
    list_page_urls = ['https://tabelog.com/' + prefecture + '/rstLst/' +
                      str(index + 1) for index in range(page_num)]
    names = []
    for list_page_url in list_page_urls:
        response = requests.get(list_page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        rst_name_targets = soup.find_all(
            'a', class_='list-rst__rst-name-target')
        [names.append(name_target.text) for name_target in rst_name_targets]
        sleep(1)
    return names


print(get_scraping_data('kanagawa', 2))
