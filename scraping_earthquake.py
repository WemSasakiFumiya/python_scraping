from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
load_dotenv()

key = os.environ['GSS_KEY']
outh_file = 'gss_credential.json'
slash = ' / '


def create_text(data):
    text = data[0] + slash + data[1] + slash + data[2] + \
        slash + data[3] + slash + data[4] + slash + \
        data[5] + slash + data[6] + '\n\n'
    return text


def get_gss_workbook():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    c = ServiceAccountCredentials.from_json_keyfile_name(outh_file, scope)
    gs = gspread.authorize(c)
    return gs.open_by_key(key)


options = Options()
options.add_argument('--headless')
options.add_argument("--no-sandbox")


class Scr():
    def __init__(self, filter_field, filter_number, file_name):
        self.filter_field = filter_field
        self.filter_number = filter_number
        self.file_name = file_name

    def geturl(self):
        wb = get_gss_workbook()
        urls = []
        scraiping_data = [['地震検知日時', '緯度', '経度',
                           'マグニチュード', '震源の深さ', '震央地名', 'Google Map Url']]
        driver = webdriver.Chrome(options=options)
        driver.get('https://www.data.jma.go.jp/multi/quake/index.html?lang=jp')
        time.sleep(1)
        seleniums = driver.find_elements(By.TAG_NAME, 'tr')
        titles = seleniums[0].text.split(' ')
        select_field_index = titles.index(self.filter_field)
        for index, value in enumerate(seleniums[2:], 2):
            seleniums_td = value.find_elements(By.TAG_NAME, "td")
            contents = [value.text for value in seleniums_td]
            content = contents[select_field_index]
            condition_number = float(content) if self.filter_field == 'マグニチュード' else int(
                content[2]) if not content == '-' else 0
            if condition_number >= self.filter_number:
                url = seleniums_td[0].find_element(
                    By.TAG_NAME, 'a').get_attribute('href')
                urls.append(url)
        for url in urls:
            driver.get(url)
            time.sleep(1)
            seleniums_detail_page = driver.find_elements(By.TAG_NAME, 'tr')
            detail_contents = seleniums_detail_page[1].find_elements(
                By.TAG_NAME, 'td')
            latitude = '.'.join(re.findall(r"\d+", detail_contents[1].text))
            longitude = '.'.join(re.findall(r"\d+", detail_contents[2].text))
            lan_with_lon = str(latitude) + ',' + str(longitude)
            google_map_url = 'https://maps.google.com/maps?ll=' + \
                lan_with_lon + '&q=' + lan_with_lon + '&z=10'
            detail_data = [content.text for content in detail_contents]
            detail_data.append(google_map_url)
            scraiping_data.append(detail_data)
            print(scraiping_data)
        driver.quit()
        if len(scraiping_data) > 0:
            f = open('earthquake_info/' + self.file_name + '.txt', 'a')
            for page_data in scraiping_data:
                f.write(create_text(page_data))
            f.close()
            ws_titles = [ws.title for ws in wb.worksheets()]
            if not (self.file_name in ws_titles):
                wb.add_worksheet(self.file_name, rows=len(
                    scraiping_data) + 5, cols=10)
            wb.values_append(self.file_name, {'valueInputOption': 'USER_ENTERED'}, {
                'values': scraiping_data})


sc = Scr('マグニチュード', 5, 'test')
sc.geturl()
