import requests
from bs4 import BeautifulSoup
from time import sleep
import os
from dotenv import load_dotenv
load_dotenv()

key = os.environ['GSS_KEY']

# colabでの認証許可するためのコード

# from google.colab import auth
# auth.authenticate_user()

# import gspread
# from google.auth import default
# creds, _ = default()
# gc = gspread.authorize(creds)

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
            detail_data = [title, img_url, address, phone_num]
            detail_data_list.append(detail_data)
            sleep(1)
    file = open('prefectures/' + prefecture + '.txt', 'a')
    for detail_data in detail_data_list:
        file.write('タイトル：' + detail_data[0] + '\n' + '画像：' +
                   detail_data[1] + '\n' + '住所：' + detail_data[2] +
                   '\n' + '電話番号：' + detail_data[3] + '\n\n')
    file.close()
    book = gc.open_by_key(key)
    sheet_titles = [sheet.title for sheet in book.worksheets()]
    sheet = book.add_worksheet(prefecture, rows=len(detail_data_list), cols=5) if not (
        prefecture in sheet_titles) else book.worksheet(prefecture)
    sheet.append_rows(detail_data_list)
    return detail_data_list


print(get_scraping_data('saitama', 1))
