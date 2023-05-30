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


def create_driver(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def get_elements(seleniums, tag_name):
    return seleniums.find_elements(By.TAG_NAME, tag_name)


def create_condition_number(content, filter_field):
    return float(content) if filter_field == 'マグニチュード' else int(
        content[2]) if content != '-' else 0


def get_url(selenium):
    return selenium.find_element(
        By.TAG_NAME, 'a').get_attribute('href')


def create_coordinate(contents):
    latitude = '.'.join(re.findall(r"\d+", contents[1].text))
    longitude = '.'.join(re.findall(r"\d+", contents[2].text))
    return str(latitude) + ',' + str(longitude)


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
        driver = create_driver(
            'https://www.data.jma.go.jp/multi/quake/index.html?lang=jp')
        time.sleep(1)
        seleniums = get_elements(driver, 'tr')
        titles = seleniums[0].text.split(' ')
        select_field_index = titles.index(self.filter_field)
        for i, value in enumerate(seleniums[2:], 2):
            seleniums_td = get_elements(value, 'td')
            contents = [value.text for value in seleniums_td]
            content = contents[select_field_index]
            condition_number = create_condition_number(
                content, self.filter_field)
            if condition_number >= self.filter_number:
                url = get_url(seleniums_td[0])
                urls.append(url)
        for url in urls:
            driver.get(url)
            time.sleep(1)
            seleniums_detail_page = get_elements(driver, 'tr')
            detail_contents = get_elements(seleniums_detail_page[1], 'td')
            coordinate = create_coordinate(detail_contents)
            google_map_url = 'https://maps.google.com/maps?ll=' + \
                coordinate + '&q=' + coordinate + '&z=10'
            detail_data = [content.text for content in detail_contents]
            detail_data.append(google_map_url)
            scraiping_data.append(detail_data)
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


select_filter_field = ['マグニチュード', '最大震度']
sc = Scr(select_filter_field[1], 2, 'max')
sc.geturl()
