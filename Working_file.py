"""
Used to call the functions 
"""

from Tenders_database_analysis_functions import find_missing_clients_in_database, get_clients_errors, complete_main_database, create_excel_sheet_with_all_no_downloads
from Functions_web_page import get_driver, download_multiple_pdf, downloads_pdf
from Functions_clients_database import read_clients_name
def generate_bc_key_words():
    #item[x] because sometimes no item name, even hidden in page - item[1], item[2],... unusual, so we want to download and look
    return ["battery charger", "battery charging", "charging modules",  "transrectifier", "DC_UPS", "installation charge", "inverter", "FCBC charger", "Battery accessories", "Battery charg"]

def download_missing_clients(df, oldest_date, key_words_list):
    missing_clients = find_missing_clients_in_database(df)
    print("Missing clients that will be downloaded", missing_clients)
    driver = get_driver()
    download_multiple_pdf(driver, missing_clients, oldest_date, key_words_list)
    print("Download missing clients finished")

def download_clients_with_errors(df, oldest_date, key_words_list):
    clients_looked_up_with_errors = get_clients_errors(df)
    print("Error clients that will be downloaded", clients_looked_up_with_errors)
    driver = get_driver()
    download_multiple_pdf(driver, clients_looked_up_with_errors, oldest_date, key_words_list)
    print("Download error clients finished")


if __name__ == "__main__":
    driver = get_driver()
    downloads_pdf(driver, "ministry", ["MINISTRY OF DEFENCE", "DEFENCE INNOVATION ORGANISATION"])
     
