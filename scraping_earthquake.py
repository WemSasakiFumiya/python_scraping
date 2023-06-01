from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

options = Options()
options.add_argument('--headless')
options.add_argument("--no-sandbox")


def create_driver(url):
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def get_elements(seleniums, tag_name):
    return seleniums.find_elements(By.TAG_NAME, tag_name)


def create_condition_number(content, filter_field):
    return float(content) if filter_field == 'マグニチュード' else int(
        content[2]) if content != '-' else 0


def get_scraping_data(filter_field, filter_number):
    driver = create_driver(
        'https://www.data.jma.go.jp/multi/quake/index.html?lang=jp')
    time.sleep(1)
    seleniums = get_elements(driver, 'tr')
    titles = seleniums[0].text.split(' ')
    select_field_index = titles.index(filter_field)
    for i, value in enumerate(seleniums[2:], 2):
        seleniums_td = get_elements(value, 'td')
        contents = [value.text for value in seleniums_td]
        content = contents[select_field_index]
        condition_number = create_condition_number(
            content, filter_field)
        if condition_number >= filter_number:
            print(content)

    driver.quit()


get_scraping_data('マグニチュード', 5)
