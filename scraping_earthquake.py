from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

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



def main(filter_field, filter_number):
    urls = []
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
        detail_page_elements = get_elements(driver, 'tr')
        detail_element = get_elements(detail_page_elements[1], 'td')
        for element in detail_element:
            print(element.text)

    driver.quit()


main('マグニチュード', 5)
