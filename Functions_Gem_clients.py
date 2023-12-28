from Functions_web_page import get_driver
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import json


def scrapping_client_name():
    gem_clients_dictionnary = {}
    driver = get_driver()
    driver.get('https://bidplus.gem.gov.in/advance-search')
    time.sleep(5)
    ministry_radio_button = driver.find_element(By.XPATH,'//*[@id="ministry-tab"]')
    ministry_radio_button.click()
    ministry_dropdown = Select(driver.find_element(By.XPATH,'//*[@id="ministry"]'))
    for option in ministry_dropdown.options[1:]:
        ministry_name = f"{option.text}"
        ministry_dropdown.select_by_visible_text(ministry_name)
        print("ministry name", ministry_name)
        time.sleep(1)
        organization_list = []
        organization_dropdown = Select(driver.find_element(By.XPATH,'//*[@id="organization"]'))
        for option_2 in organization_dropdown.options[1:]:
            organization_name = option_2.text
            organization_list.append(organization_name)
            print("organization name", organization_name)
        gem_clients_dictionnary[ministry_name] = organization_list
        print(gem_clients_dictionnary)
    

    with open("clients"+ '.json', 'w') as fichier:
        json.dump(gem_clients_dictionnary, fichier, indent=4)  # Écrit le dictionnaire formaté en JSON
    print("done")


def read_clients_name(file_name):
    with open(file_name + '.json', 'r') as file:
        return json.load(file)


