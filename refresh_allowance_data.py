import threading
import os
from time import sleep
from selenium import webdriver
import pandas
import numpy as np

DOWNLOADED_FILES_DESTINATION = os.getcwd() + '/data'
ALLOWANCE_DATA_PATH = DOWNLOADED_FILES_DESTINATION + "/EMBER_Coal2Clean_EUETSPrices.csv"

# HISTORY_LENGTH = 31 * 3
HISTORY_LENGTH = 100 * 3

allowance_data_past_week = np.full(HISTORY_LENGTH, 1)
allowance_condition = threading.Condition()

DATA_UPDATE_INTERVAL = 60 * 60 # Seconds


HEADLESS = True

def generate_chrome_settings(headless):
    option = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOADED_FILES_DESTINATION}
    option.add_experimental_option("prefs", prefs)

    if headless:
        option.add_argument('--headless')

    return option


def download_file():
    print("Downloading allowance data...")
    driver = webdriver.Chrome('./chromedriver', options=generate_chrome_settings(HEADLESS))
    url = "https://QU6FEUWMSKTSIJSJ.anvil.app/FUIY7TKGIS7A33N4XOCB7YM2"
    driver.get(url)

    eu_button = None
    sleep(10)

    while eu_button is None:
        results = driver.find_elements('class name', 'button-text')
        if len(results) > 0:
            eu_button = results[0]
            break

    eu_button.click()
    sleep(10)
    driver.close()
    print("Download successful!")

def update_allowance_data():
    print("Loading allowance data...")
    svg_data = pandas.read_csv(ALLOWANCE_DATA_PATH)['Price'].to_numpy()[-HISTORY_LENGTH:]

    allowance_condition.acquire()
    global allowance_data_past_week
    allowance_data_past_week = svg_data
    allowance_condition.release()

    print("Load successful!")

def update_allowance_data_regularly():
    while True:
        download_file()
        update_allowance_data()  # TODO: Fix a mutex.
        sleep(DATA_UPDATE_INTERVAL)


def start_allowance_data_updater():
    th = threading.Thread(target=update_allowance_data_regularly)
    th.start()

if __name__ == "__main__":
    download_file()
    update_allowance_data()
