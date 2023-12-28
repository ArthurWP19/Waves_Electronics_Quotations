from Functions_web_page import wait_until_all_tenders_charged, get_driver, filter_name, charging_web_page, get_to_first_page, read_item_name, downloads_pdf
from Functions_web_page import download_multiple_pdf
import selenium 
from selenium.webdriver.common.by import By
from Functions_Gem_clients import read_clients_name
from database_analysis_functions import database_report, read_gem_download_file, get_clients_looked_up

def test_charging_web_page():
    driver = get_driver()
    charging_web_page(driver, "ministry", ["MINISTRY OF DEFENCE", "GOA SHIPYARD LIMITED"])
    wait_until_all_tenders_charged(driver)
    n_tenders = len(driver.find_elements(By.CLASS_NAME, "card"))
    print("n_tenders on page", n_tenders)
    #Downloading all tenders if date superieur or equal to oldest_date 
    for n_tender in range (2,2 + n_tenders):
        #filter item_name: read item_name 
        item_name = driver.find_elements(By.XPATH, f'/html/body/section[3]/div/div/div/div[{n_tender}]/div[3]/div/div[1]/div[1]/a')[0].get_attribute("data-content")
        print("item_name", item_name)
        input("next item, press enter")

def test_downloads_pdf():
    driver = get_driver()
    bc = generate_bc_key_words()
    #clients = read_clients_name(r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\clients")
    #railway_clients = clients["MINISTRY OF RAILWAYS"]
    #for client in railway_clients:
    downloads_pdf(driver, "ministry",["MINISTRY OF DEFENCE","INDIAN ARMY"], oldest_date= "01-01-1999", last_page = 99, key_word_list = bc, authorized_approx = 2)
    print("finished")



    """
    #try: 
    downloads_pdf(driver, "ministry",["MINISTRY OF DEFENCE", "HINDUSTAN SHIPYARD LIMITED (HSL)"], oldest_date= "01-01-1999", last_page = 99, key_word_list = key_words)
    #except Exception as e:
     #   print(e)
      #  print ("HINDUSTAN SHIPYARD LIMITED (HSL) didn't work")
    #time.sleep(10)
    
    try: 
        downloads_pdf(driver, "ministry",["MINISTRY OF DEFENCE", "GARDEN REACH SHIP BUILDERS AND ENGINEERS LIMITED (GRSE)"], oldest_date= "01-01-1999", last_page = 99, key_word_list = key_words)
    except Exception as e:
        print(e)
        print ("GARDEN REACH SHIP BUILDERS AND ENGINEERS LIMITED (GRSE) didn't work")
    time.sleep(10)
    
    try: 
        downloads_pdf(driver, "ministry",["MINISTRY OF DEFENCE", "MAZAGON DOCK SHIPBUILDERS LIMITED"], oldest_date= "01-01-1999", last_page = 99, key_word_list = key_words)
    except Exception as e:
        print(e)
        print ("MAZAGON DOCK SHIPBUILDERS LIMITED didn't work")
    """
    print("successful")

def test_no_tender():
    driver = get_driver()
    downloads_pdf(driver, "ministry",["MINISTRY OF DEFENCE", "MAZAGON DOCK SHIPBUILDERS LIMITED"], oldest_date= "01-01-1999", last_page = 99)


def go_back_to_page_one(driver):
    if len(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[2]"))!= 0:
        button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[2]")[0]
        button.click()
        wait_until_all_tenders_charged(driver)
    elif len(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[10]/a[2]")) != 0:
        button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[10]/a[2]")[0]
        button.click()
        wait_until_all_tenders_charged(driver)
    else:
        button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[11]/a[2]")[0] 
        button.click()
        wait_until_all_tenders_charged(driver)

def test_get_to_first_page():
    driver = get_driver()
    charging_web_page(driver, "ministry", ["MINISTRY OF DEFENCE", "HINDUSTAN AERONAUTICS LIMITED (HAL)"])
    get_to_first_page(driver, 21)
    input("enter")

def test_filter_name():
    item_name = "Items: PAINTS FOR FLOATING DOCK"
    key_word_list = ["paint"]
    print(filter_name(item_name, key_word_list, authorized_approx = 2))

def test_read_item():
    driver = get_driver()
    charging_web_page(driver, "ministry", ["MINISTRY OF DEFENCE", "MAZAGON DOCK SHIPBUILDERS LIMITED"])
    input("enter")
    x_path_card_web_element = "/html/body/section[3]/div/div/div/div[4]"
    print(read_item_name(driver, x_path_card_web_element))


def generate_bc_key_words():
    #item[x] because sometimes no item name, even hidden in page - item[1], item[2],... unusual, so we want to download and look
    return ["battery charger", "battery charging", "charging modules",  "transrectifier", "DC_UPS", "installation charge", "inverter", "FCBC charger", "Battery accessories", "Battery charg"]

def test_download_multiple_pdf():
    driver = get_driver()
    bc_key_words =generate_bc_key_words()
    clients_database = read_clients_name(r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\clients")
    database_path = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\Gem_tenders_database\23-12-2023- Gem_tenders_database.xlsx"
    database_path_2 = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\Downloads GEM 23-12-2023\23-12-2023 - GeM downloads.xlsx"
    df = read_gem_download_file(database_path)
    clients_looked_up = get_clients_looked_up(df)
    df_2 = read_gem_download_file(database_path_2)
    clients_looked_up_2 = get_clients_looked_up(df_2)
    for ministry in clients_database.keys():
        if ministry not in clients_looked_up.keys() and ministry not in clients_looked_up_2.keys():
            download_multiple_pdf(driver, {ministry : clients_database[ministry]}, "01-01-2000",bc_key_words)
        """
        else:    
            if len(clients_database[ministry]) != len(clients_looked_up[ministry]):
                organisation_to_look = []
                for orga in clients_database[ministry]:
                    if orga not in clients_looked_up[ministry]:
                        organisation_to_look.append(orga)
                print("ministry", ministry)
                print("organisation to look", organisation_to_look)
                download_multiple_pdf(driver, {ministry : organisation_to_look}, "01-01-2000",bc_key_words)
        """
        print("all finished")





if __name__ == "__main__":
    test_download_multiple_pdf()