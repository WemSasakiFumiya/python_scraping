from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
load_dotenv()


# スクレイピング

tabelog = 'https://tabelog.com/'
page_list = '/rstLst/'
key = os.environ['GSS_KEY']
outh_file = 'gss_credential.json'


def create_text(no, title, img, address, phone):
    text = 'No：' + no + '\n' + 'タイトル：' + title + '\n' + '画像：' + \
        img + '\n' + '住所：' + address + '\n' + '電話番号：' + phone + '\n\n'
    return text


def get_gss_workbook():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    c = ServiceAccountCredentials.from_json_keyfile_name(outh_file, scope)
    gs = gspread.authorize(c)
    return gs.open_by_key(key)


class Scr():
    def __init__(self, prefecture, page_num):
        self.urls = [tabelog + prefecture + page_list +
                     str(index + 1) for index in range(page_num)]
        self.prefecture = prefecture

    def geturl(self):
        wb = get_gss_workbook()
        scraping_data_dictionary = []
        scraping_data_list = []
        no = 0
        with ThreadPoolExecutor() as executor:
            contents = list(executor.map(requests.get, self.urls))
        for content in contents:
            soup = BeautifulSoup(content.content, 'html.parser')
            place_page_url = soup.find_all(
                'a', class_='list-rst__rst-name-target')
            page_urls = [x.get('href') for x in place_page_url]
            with ThreadPoolExecutor() as executor:
                page_contents = list(executor.map(requests.get, page_urls))
            for i, content in enumerate(page_contents):
                soup = BeautifulSoup(content.content, 'html.parser')
                no += 1
                title = soup.find('meta', property='og:title').get('content')
                img = soup.find(
                    'img', class_='p-main-photos__slider-image').get('src')
                address = soup.find('p', class_='rstinfo-table__address')
                phone = soup.find('strong', class_='rstinfo-table__tel-num')
                data = {'no': no, 'title': title, 'img': img,
                        'address': address.text, 'phone': phone.text}
                scraping_data_dictionary.append(data)
                scraping_data_list.append(list(data.values()))
                print(str(no) + '：' + title)
                # sleep(1)

        f = open('prefecture/' + self.prefecture + '.txt', 'a')
        for pageUrl in scraping_data_dictionary:
            f.write(create_text(
                str(pageUrl['no']), pageUrl['title'], pageUrl['img'], pageUrl['address'], pageUrl['phone']))
        f.close()
        ws_titles = [ws.title for ws in wb.worksheets()]
        if not (self.prefecture in ws_titles):
            wb.add_worksheet(self.prefecture, rows=no + 10, cols=10)
        wb.values_append(self.prefecture, {'valueInputOption': 'USER_ENTERED'}, {
                         'values': scraping_data_list})
        # return scraping_data


sc = Scr('toyama', 1)
sc.geturl()
