from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')


def create_driver(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def get_elements(elements, tag_name):
    return elements.find_elements(By.TAG_NAME, tag_name)


def create_condition_number(selected_field, filter_field):
    return float(selected_field) if filter_field == 'マグニチュード' else int(
        selected_field[2]) if selected_field != '-' else 0


def get_url(element):
    return element.find_element(
        By.TAG_NAME, 'a').get_attribute('href')


def create_coordinate(contents):
    latitude = '.'.join(re.findall(r"\d+", contents[1].text))
    longitude = '.'.join(re.findall(r"\d+", contents[2].text))
    return latitude + ',' + longitude


slash = ' / '


def create_text(data):
    text = data[0] + slash + data[1] + slash + data[2] + \
        slash + data[3] + slash + data[4] + slash + \
        data[5] + slash + data[6] + '\n\n'
    return text


def main(filter_field, filter_number, file_name):
    urls = []
    scraiping_data = [['地震検知日時', '緯度', '経度',
                       'マグニチュード', '震源の深さ', '震央地名', 'Google Map Url']]
    driver = create_driver(
        'https://www.data.jma.go.jp/multi/quake/index.html?lang=jp')
    time.sleep(2)
    elements = get_elements(driver, 'tr')
    titles = elements[0].text.split(' ')
    select_field_index = titles.index(filter_field)
    for i, content in enumerate(elements[2:], 2):
        elements_td = get_elements(content, 'td')
        fields = [element.text for element in elements_td]
        selected_field = fields[select_field_index]
        condition_number = create_condition_number(
            selected_field, filter_field)
        if condition_number >= filter_number:
            url = get_url(elements_td[0])
            urls.append(url)
    for url in urls:
        driver.get(url)
        time.sleep(2)
        detail_elements_tr = get_elements(driver, 'tr')
        detail_elements_td = get_elements(detail_elements_tr[1], 'td')
        coordinate = create_coordinate(detail_elements_td)
        google_map_url = 'https://maps.google.com/maps?ll=' + \
            coordinate + '&q=' + coordinate + '&z=10'
        detail_fields = [element.text for element in detail_elements_td]
        detail_fields.append(google_map_url)
        scraiping_data.append(detail_fields)

    if len(scraiping_data) > 0:
        file = open('earthquake_info/' + file_name + '.txt', 'a')
        for data_to_write in scraiping_data:
            file.write(create_text(data_to_write))
        file.close()
    book = gc.open_by_key(key)
    sheet_titles = [sheet.title for sheet in book.worksheets()]
    sheet = book.add_worksheet(file_name, rows=len(scraiping_data), cols=5) if not (
        file_name in sheet_titles) else book.worksheet(file_name)
    sheet.append_rows(scraiping_data)
    driver.quit()


main('マグニチュード', 5, 'earthquake')
