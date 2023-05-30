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


def get_scraping_data():
    driver = create_driver(
        'https://www.data.jma.go.jp/multi/quake/index.html?lang=jp')
    time.sleep(1)
    seleniums = driver.find_element(By.ID, 'header')
    return seleniums.text


print(get_scraping_data())
