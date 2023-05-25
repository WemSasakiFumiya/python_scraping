import requests
from bs4 import BeautifulSoup
from time import sleep


def get_scraping_data(prefecture, page_num):
    list_page_urls = ['https://tabelog.com/' + prefecture + '/rstLst/' +
                      str(index + 1) for index in range(page_num)]
    detail_data_list = []
    for list_page_url in list_page_urls:
        response = requests.get(list_page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        rst_name_targets = soup.find_all(
            'a', class_='list-rst__rst-name-target')
        detail_page_urls = [x.get('href') for x in rst_name_targets]
        for detail_page_url in detail_page_urls:
            detail_page_response = requests.get(detail_page_url)
            detail_page_soup = BeautifulSoup(
                detail_page_response.content, 'html.parser')
            title = detail_page_soup.find(
                'h2', class_='display-name').text.strip()
            img_url = detail_page_soup.find(
                'img', class_='p-main-photos__slider-image').get('src')
            address = detail_page_soup.find(
                'p', class_='rstinfo-table__address').text
            phone_num = detail_page_soup.find(
                'strong', class_='rstinfo-table__tel-num').text
            detail_data = {'title': title, 'img_url': img_url,
                           'address': address, 'phone_num': phone_num}
            detail_data_list.append(detail_data)
            sleep(1)
    return detail_data_list


print(get_scraping_data('kanagawa', 2))
