
from cgitb import lookup
from unittest.mock import NonCallableMock

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time 
import numpy as np
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from os import path
# import packages
import PyPDF2
import re
import os
import shutil
import xlsxwriter
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import re
import pandas as pd
import openpyxl
import traceback




###Web page functions - reading  ###

def read_tender_starting_date(driver, x_path_card_web_element):
    x_path_starting_date = x_path_card_web_element + "/div[3]/div/div[3]/div[1]/span"
    starting_date_tender = driver.find_elements(By.XPATH, x_path_starting_date)[0]
    #reading emission date as a text
    starting_date_tender = starting_date_tender.text
    #keeping only dd-mm-aa
    starting_date_tender = starting_date_tender[0:10]
    starting_date_tender = datetime.strptime(starting_date_tender,  "%d-%m-%Y").date()
    return starting_date_tender

def read_tender_end_date(driver, x_path_card_web_element):
    x_path_end_date = x_path_card_web_element + "/div[3]/div/div[3]/div[2]/span"
    end_date_tender = driver.find_elements(By.XPATH, x_path_end_date)[0]
    #reading emission date as a text
    end_date_tender = end_date_tender.text
    #keeping only dd-mm-aa
    end_date_tender = end_date_tender[0:10]
    end_date_tender = datetime.strptime(end_date_tender,  "%d-%m-%Y").date()
    return end_date_tender

def read_last_page_number(driver):
    if driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[7]")[0].text == "Next":
        last_web_page = int(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[6]")[0].text)
    else:
        last_web_page = int(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[7]")[0].text)
    return last_web_page
#One tender page:last page adress, next adress
#/html/body/section[3]/div/div/div/div[4]/span[3] : current next 
#10 tenders page : 


def read_item_name(driver, x_path_card_web_element):
    """
    card web element = one tender
    """
    head_text_path = x_path_card_web_element + "/div[3]/div/div[1]/div[1]"
    print(head_text_path)
    head_text = driver.find_elements(By.XPATH, head_text_path)[0].text
    #remove "Items:" at the beginnning:
    if head_text[:6] == "Items:":
        head_text = head_text[6:]
    else:
        raise Exception("Items: not at the begining of head_text", head_text)
        
    #if it is word, we want to access to the complete list of key words, after "...". This is stored in attribute data-content 
    print("head text", head_text)
    if is_word(head_text):
        print("head text is words", head_text)
        #only if item name is incomplete
        if head_text[-3:] == "...":
            
            item_data_path = x_path_card_web_element + "/div[3]/div/div[1]/div[1]/a"
            full_item_name = driver.find_elements(By.XPATH, item_data_path)[0].get_attribute("data-content")
            print("full_item_name", full_item_name)
        else:
            full_item_name = head_text
        
    else:
        print("head text is numbers", head_text)
        item_data_path = x_path_card_web_element + "/div[3]/div/div[1]/div[1]/a"
        full_item_name = driver.find_elements(By.XPATH, item_data_path)[0].get_attribute("title")
    return full_item_name


def is_tender(driver):
    """
    For a client
    Returns True if there is at least one tender, False if there is "no data found", which means 0 current tenders for this client 
    """
    #let some time to do the research 
    time.sleep(5)
    danger_elements = driver.find_elements(By.CLASS_NAME, "alert.alert-danger")
    is_tender = True 
    for elt in danger_elements:
        try:
            if elt.text == "No data found":
                "No data found for this client"
                is_tender = False
            else:
                print(f"WARNING: one element alert-danger in page, but not no data found type. Text available and is {elt.text}")
                input("Testing purpose - danger element on page not identified - to investigate")
        except:
            print("WARNING: one element alert-danger in page, but not no data found type, and no text available ")
            input("Testing purpose - danger element on page not identified - to investigate")
    return is_tender 


            
            
        
### Web page functions - tools ###

def wait_until_all_tenders_charged(driver, last_page = False):
    """
    If last page, structure is different 
    """
    #WebDriverWait(driver, 60).until(lambda driver: len(driver.find_elements(By.XPATH, "//body//div[@class='card']")) > 1)  #supposes that if one tender is charged, all tenders of the page are - as it is observed
    #WebDriverWait(driver, 60).until(lambda driver: len(driver.find_elements(By.XPATH, "//div[@class='section-3']//a[@class='page-link']")) > 1)#we need also buttons, which are page-link, to be charged
    #we wait for tenders to be charged (class card), suppose that if one is charged, all ten are charged. We also wait for buttons to be charged: page links in section 3
    #WebDriverWait(driver, 60).until(lambda driver: len(driver.find_elements(By.XPATH, "(//div[@class='container'])[3]")) > 0)
    if last_page:
        WebDriverWait(driver, 120).until(lambda driver: len(driver.find_elements(By.XPATH, "//body//div[@class='card']"))) > 0 
    else: 
        WebDriverWait(driver, 120).until(lambda driver: len(driver.find_elements(By.XPATH, "//body//div[@class='card']")) > 0 )
                                             #and len(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[12]")) > 0) #problems, position of button depends on number of tender on page
        time.sleep(3)                                     

def get_to_first_page(driver, last_page_number, first_page_number = 1):
     wait_until_all_tenders_charged(driver)
     if first_page_number > last_page_number:
         raise ValueError(f"User first page number {first_page_number} is above number of pages {last_page_number} on GeM website for this organisation")
     
     else:
         #if page number = 1, do nothing 
        if first_page_number == 1:
            pass 
        #if possible, go straight to the page if its number is already displayed, i.e from 2 to 5 included, or two last 
        elif first_page_number <= 5:
            button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[{first_page_number - 1}]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
             
        elif first_page_number == last_page_number:
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[6]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
             
        elif first_page_number == last_page_number - 1:
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            
        #all particular cases close to page 1 or last page
        elif first_page_number == 6:
            button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[4]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[6]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
             
        elif first_page_number == 7:
            button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[4]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[7]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
             
        elif last_page_number - first_page_number <= 4:
            diff = last_page_number - first_page_number
            #go to last_page -1 because last page does not have 10 tenders displayed --> Xpath can change 
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[{8 - diff}]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
        elif last_page_number - first_page_number == 5:
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[{4}]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
             
        elif last_page_number - first_page_number == 6:
            button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[{4}]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
            button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[4]")[0]
            button.click()
            wait_until_all_tenders_charged(driver)
             
        
        #all other cases
        else:
            #look from page 1
            if first_page_number < last_page_number //2:
                #go to page 7 - we know that first_page_number is above 7
                button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[4]")[0]
                button.click()
                wait_until_all_tenders_charged(driver)
                button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[7]")[0]
                button.click()
                wait_until_all_tenders_charged(driver)
                lookup_page = 7
                while lookup_page != first_page_number:
                    #if looked_page is just one page right from lookup_page 
                    if first_page_number - lookup_page == 1:
                        button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[6]")[0]
                        button.click()
                        lookup_page = lookup_page + 1
                        wait_until_all_tenders_charged(driver)
                        break 
                        
                    else:
                        button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[7]")[0]
                        button.click()
                        wait_until_all_tenders_charged(driver)
                        lookup_page = lookup_page + 2
                 

            else:
                #go to page last_page_number - 6
                button = driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
                button.click()
                wait_until_all_tenders_charged(driver)
                button = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[13]/a[{4}]")[0]
                button.click()
                wait_until_all_tenders_charged(driver)
                button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[4]")[0]
                button.click()
                wait_until_all_tenders_charged(driver)
                lookup_page = last_page_number - 6
                while lookup_page != first_page_number:
                    #if looked_page is just one page left from lookup_page 
                    if lookup_page - first_page_number == 1:
                        button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[5]")[0]
                        button.click()
                        wait_until_all_tenders_charged(driver)
                        break
                        
                        
                    else:
                        button = driver.find_elements(By.XPATH,"/html/body/section[3]/div/div/div/div[13]/a[4]")[0]
                        button.click()
                        wait_until_all_tenders_charged(driver)
                        lookup_page = lookup_page - 2
        pass

### Folder and excel file tools###

def create_folder(root):

    # Get today's date in DD-MM-YYYY format
    today_date = datetime.now().strftime("%d-%m-%Y")
    # Name of the folder to create
    folder_name = f"Downloads GEM {today_date}"
    # Full path of the folder
    folder_path = os.path.join(root, folder_name)
    # Check if the folder already exists
    if not os.path.exists(folder_path):
        # Create the folder if it doesn't exist
        os.makedirs(folder_path)
        print(f"Folder '{folder_name}' created successfully in '{root}'.")
    else:
        print(f"Folder '{folder_name}' already exists in '{root}'.")


def create_excel_file(root):
    """
    IF excel of downloads does not exist, create it and return correspondind dataframe
    If exists, read it and return corresponding dataframe
    """
    today_date = datetime.now().strftime("%d-%m-%Y")
    download_folder_name = f"/Downloads GEM {today_date}"
    file_name = f"/{today_date} - GeM downloads.xlsx"
    if os.path.exists(root + download_folder_name +  file_name):
        print(f"Excel file {file_name} already exists. No action taken.")
        df = pd.read_excel(root + download_folder_name +  file_name, sheet_name='Sheet1', header=0)
        print("excel columns", df.columns)
        if list(df.columns) != ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name","Downloaded", "Key word that filtered item", "Starting date", "End date"]:
            raise ValueError(f"Existing file {root + download_folder_name +  file_name} does not match template of columns:Download date, Ministry, Organisation, Bid's ID, Item name, Downloaded , Key word that filtered item","Starting date", "End date")
    # Create a new Excel workbook
    else:
        print("creating excel file")
        # Write to the specified cells
        values = ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name", "Downloaded", "Key word that filtered item", "Starting date", "End date"]
        df = pd.DataFrame(columns=values)
        # Save the Excel file
        with pd.ExcelWriter(root + download_folder_name + file_name, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False, header=True, startrow=0)
    
        print("excel file saved successfully")


    file_path = root + download_folder_name + file_name
    print("OUTPUT", df, file_path)
    return df, file_path
    

### Other tools###

def convert_lowercase(input_string):
    result = ''
    for char in input_string:
        if char.isupper():
            result += char.lower()
        else:
            result += char
    return result


def filter_name(item_name, key_word_list = [], authorized_approx = 2):
    """
    key_word_list: if several words in one string, means and (ex: "battery charger")
    supposes that item_name is made of words (not numbers), as an output of read_item_name function
    returns a boolean, True if in key_word_list, False if not
    if key_word_dict is empty, we don't filter
    authorized approx: number of differences authorized between item_name and key_words from list
    if there are words in item_name, if none of item_name word is in key_word list, we don't keep
    

    """
    if key_word_list == []:
        return True, None
    else:
        #parsing the item_name, using coma or space or - or _ as separator
        parsed_item_name = re.split(r'[, \t_\-&]+', item_name)
        #delete Na elements if any
        parsed_item_name = [item for item in parsed_item_name if item]
        print("parsed_item_name", parsed_item_name)
        for key_word in key_word_list:
            parsed_key_word = key_word.split()
            common_words = []
            print(parsed_key_word)
            for sub_key_word in parsed_key_word:
                sub_key_word = convert_lowercase(sub_key_word)
                for word in parsed_item_name:
                    word = convert_lowercase(word)
                    differences = sum(c1 != c2 for c1, c2 in zip(word, sub_key_word))
                    if differences + abs(len(word) - len(sub_key_word)) <= authorized_approx and sub_key_word not in common_words:
                        print(f"{word} and {sub_key_word} are close")
                        common_words.append(sub_key_word)
            print(common_words, parsed_key_word)
            if len(common_words) == len(parsed_key_word):
                return True, key_word

    return False, None 



def is_word(head_text):
    """
    Two types of Item names in page tenders:
    --> Items: word1, word2,...: returns true
    --> Items: number1, number2,...: returns false
    CAUTIOUS: presence of "..." in the head text after a few words/numbers. 
    """
    parsed_head_text = re.split(r'[, \t_\-:]+', head_text)
    #delete Na elements if any
    parsed_head_text = [item for item in parsed_head_text if item]
    number_of_not_word = 0
    for word in parsed_head_text:
        word = convert_lowercase(word)
        #if word only made of float or int, or float and int +...", " means that it's not a word
        if re.match(r'^[+-]?\d+(\.\d+)?|\d+\.\.\.$|\.\.\.$', word):
            number_of_not_word += 1
    if len(parsed_head_text) == number_of_not_word:
        return False
    else:
        return True

### Main Functions ###
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=C:\Users\arthu\AppData\Local\Google\Chrome\User Data\Profile 2") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome()
    return driver

def charging_web_page(driver):
    driver.get('https://bidplus.gem.gov.in/advance-search')
    time.sleep(5)


def research(driver, page_type,page_info):
    start_charging_time = time.time()
    if page_type=="ministry":
        ministry_name,client=page_info[0],page_info[1]
        # Click on the "Search by ministry / organisation" option
        ministry_radio_button = driver.find_element(By.XPATH,'//*[@id="ministry-tab"]')
        ministry_radio_button.click()
        time.sleep(1)

        # Select the ministry
        ministry_dropdown = Select(driver.find_element(By.XPATH,'//*[@id="ministry"]'))
        ministry_dropdown.select_by_visible_text(ministry_name);
        time.sleep(1)


        #Select the organisation 
        ministry_dropdown = Select(driver.find_element(By.XPATH,'//*[@id="organization"]'))
        ministry_dropdown.select_by_visible_text(client);
        time.sleep(1)

        # Click on the "Search " option
        search_button = driver.find_element(By.XPATH,'/html/body/section[2]/div/div[2]/div/div[2]/div[2]/div[1]/form/div[4]/div[1]/a[1]')
        search_button.click()
        time.sleep(3)
        
        #printing the number of tenders to be download
        try:
            numberBids = driver.find_element(By.XPATH,'//*[@id="bidCard"]/div[1]/div/span').get_attribute("textContent")
            print("For " + client + ", "+ str(numberBids)+ " are expected")
        except:
            return(False)

    if page_type=="state":
        state_name=page_info
        # Click on the "Search by consignee location" option
        location_radio_button = driver.find_element(By.XPATH,'//*[@id="location-tab"]')
        location_radio_button.click()
        time.sleep(1)

        # Select the state
        state_dropdown = Select(driver.find_element(By.XPATH,'//*[@id="state_name_con"]'))
        state_dropdown.select_by_visible_text(state_name)
        time.sleep(1)


        # Click on the "Search " option
        search_button = driver.find_element(By.XPATH,'/html/body/section[2]/div/div[2]/div/div[2]/div[3]/div/form/div[3]/div[1]/a[1]')
        search_button.click()
        time.sleep(3)
        
        #printing the number of tenders to be download
        numberBids = driver.find_element(By.XPATH,'//*[@id="bidCard"]/div[1]/div/span').get_attribute("textContent")

        print("For " + state_name + ", "+ str(numberBids)+ " are expected")
    #input()
    end_charging_time = time.time()
    print(f"***Time for charging web page was {end_charging_time - start_charging_time}s**\\")
    wait_until_all_tenders_charged(driver)
    print("charging page over")
    return(True)





def downloads_pdf(driver, page_type, page_info, oldest_date = "01-01-2000", first_page = 1, last_page = 99,  key_word_list = [], authorized_approx = 2, networkQualitySleepingTime = 3, root = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app",
                  download_directory = "C:/Users/arthu/Downloads"):
    """
    oldest date: expected string "dd-mm-aaaa": all tenders EMITTED AFTER emission date will be downloaded 
    first_page: no of the first page to look after research
    stop_page: no of the page to stop. stop_page should be superior to firs-page
    """
    # Getting current time and hour, for labelling 
    date_time = datetime.now()
    curent_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    ##creating folder to stock downloads 
    create_folder(root)
    downloads_register, download_register_path = create_excel_file(root)
    intermediate_downloads_register = pd.DataFrame(columns = ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name", "Downloaded", "Key word that filtered item", "Starting date", "End date"])
    if first_page > last_page:
        raise ValueError(f"First page input {first_page} shall not be superior to last page input {last_page}")
    # Initialisation of variable for files transfer
    list_file=[]
    #initializing driver and charging web page
    try:
    
        charging_web_page(driver)
        research(driver, page_type, page_info)
        #checking is there are tenders on page. 
        if not is_tender(driver):
            print(f"No data_found for the client {page_info}")
            new_row = [curent_time, page_info[0], page_info[1], "NO DATA FOUND ON GEM WEBSITE", None, None, None, None, None]
            intermediate_downloads_register.loc[len(intermediate_downloads_register)] = new_row
        else:
            n_page_to_read = last_page - first_page
            # going to the first page given as an input by the user 
            get_to_first_page(driver, last_page, first_page)
            downloaded_bids = []
            last_page_done = False
            i = 0
            #3 conditions to stop loop: either too much pages looked up (100), or we read the pages we had to read, or we reached the last page on Gem
            while i < 100 and i < n_page_to_read + 1 and not last_page_done:
                page_hyplist = []
                wait_until_all_tenders_charged(driver, last_page)
                #finding the number of tenders on page - usually it's ten, except for the last one
                n_tenders = len(driver.find_elements(By.CLASS_NAME, "card"))
                if n_tenders < 10:
                    last_page_done = True
                print("n_tenders on page", n_tenders)
                #Downloading all tenders if date superieur or equal to oldest_date 
                for n_tender in range (2,2 + n_tenders):
                    x_path_tender = f"/html/body/section[3]/div/div/div/div[{n_tender}]"
                    starting_date_tender = read_tender_starting_date(driver, x_path_tender)
                    end_date_tender = read_tender_end_date(driver, x_path_tender)
                    oldest_date_tender = datetime.strptime(oldest_date,  "%d-%m-%Y").date()
                    if starting_date_tender >= oldest_date_tender:
                        #filter item_name: read item_name 
                        item_name= read_item_name(driver, x_path_tender)
                        #get name of bid on GeM website: only 7 number ID
                        name_bid = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[{n_tender}]/div[1]/p[1]/a")[0].text[-7:]
                        #get name of the file that is downloaded when we click on the bid - NOT THE SAME AS GEM BID NAME. ONLY 7 number ID
                        file_name = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[{n_tender}]/div[1]/p[1]/a")[0].get_attribute("href")[-7:]
                        boolean, key_word = filter_name(item_name, key_word_list, authorized_approx)
                        #dictionnary: key name of file, value: [bid_name, hyperlink, item_name, key_word, starting_date, end_date]
                        file = {file_name: [name_bid, driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[{n_tender}]/div[1]/p[1]/a")[0], item_name, key_word, starting_date_tender, end_date_tender]}
                        if boolean: 
                            #GeM portal is having an issue : Sometimes, some tenders are put twice in the list on different pages
                            #We keep track of the bids we already downloaded in downloaded_bids, so we don't click on them again
                            print("**NAME_BID**", name_bid, downloaded_bids, "\\")
                            if name_bid not in downloaded_bids: 
                                page_hyplist.append(file)
                                downloaded_bids.append(name_bid)
                                new_row = [curent_time, page_info[0], page_info[1], file[file_name][0], file[file_name][2], "Yes", file[file_name][3], file[file_name][4], file[file_name][5]]
                                intermediate_downloads_register.loc[len(intermediate_downloads_register)] = new_row
                            else:
                                print(f"Bid {name_bid} already downloaded")
                        else:
                            #write in csv screened names that we did not download 
                            new_row = [curent_time, page_info[0], page_info[1], file[file_name][0], file[file_name][2], "No", file[file_name][3], file[file_name][4], file[file_name][5]]
                            intermediate_downloads_register.loc[len(intermediate_downloads_register)] = new_row

                print("DOWNLOADING")
                
                for file in page_hyplist:
                    try :
                        for file_name in file.keys():
                            #catch hyperlink 
                            elem = file[file_name][1]
                            elem.click()
                            wait_until_all_tenders_charged(driver, last_page)
                            #create and append bid information to download register
                            
                    except NoSuchElementException :
                        print(f"Erreur, bid {file_name} not clickable on page")
                        continue
                #Renaming files with GeM: bid name, mooving them to day download file 

                #first wait for all files to be downloaded - allow several trials 
                time.sleep(4)
                n_attempt = 0
                print("downloaded bids", downloaded_bids)

                print("RENAMING FILES")
                for n_attempt in range(11):
                    #if not able to download everything after 10 attempts, we move to the next page. 
                    if n_attempt == 10:
                        print(f"All files of page {first_page + i} not downloaded after 10 attempts. Go to next page")
                        break 
                    try: 
                        #if try to rename a file that was already renamed in previous attempt, error 
                        renamed_files = []   
                        for file in page_hyplist:
                            for file_name in file.keys():
                                downloaded_file_name = os.path.join(download_directory, f"GeM-Bidding-{file_name}.pdf")
                                bid_name = os.path.join(os.path.dirname(download_register_path) , f"GeM-Bidding-{file[file_name][0]}.pdf")
                                #pathological case: if the same page is looped in two different executions, with different keyword, but one same offer was already downloaded
                                #for keyword1
                                if not os.path.exists(bid_name):
                                    os.rename(downloaded_file_name, bid_name)
                                    renamed_files.append(file)
                                    print(f"file {file_name} as been renamed to {file[file_name][0]}")
                                else:
                                    os.remove(downloaded_file_name)
                                    print(print(f"file {file_name} has been downloaded during another execution"))
                            #if file not found, probably because download not finished
                    except FileNotFoundError as e:  
                            print(f"File {downloaded_file_name} not found: {e}")
                            print(f"Attempt {n_attempt + 1}: all files were not downloaded, waiting 5s")
                            time.sleep(5)
                    #if able to rename all files, we leave this loop
                    else:
                        break 
                    page_hyplist = [file for file in page_hyplist if file not in renamed_files]
                    print(len(page_hyplist))


                #waiting before going to next page
                time.sleep(networkQualitySleepingTime)

                #NExt page (if we are not at the last that has to be read)
                if not last_page_done:
                    next_button=driver.find_element(By.XPATH,'//*[@class="page-link next"]')
                    next_button.click()
    except Exception as e:
        print(f"An error {type(e).__name__} occured for client {page_info}")
        traceback.print_exc()
        new_row = [curent_time, page_info[0], page_info[1], f"Error {type(e).__name__} occured", None, None, None, None, None]
        intermediate_downloads_register.loc[len(intermediate_downloads_register)] = new_row


    #update csv 
    updated_downloads_register = pd.concat([downloads_register, intermediate_downloads_register]).reset_index(drop=True)
    updated_downloads_register.to_excel(download_register_path, index=False, header = True)
    print(f"{page_info[0], page_info[1]} FINISHED")
    #closes web page
    return list_file


def download_multiple_pdf(driver, clients:dict, oldest_date = "01-01-2000", key_words_list = [], authorized_approx = 2,  networkQualitySleepingTime = 3, root = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app" ,
                  download_directory = "C:/Users/arthu/Downloads"):
    """
    clients: {ministry: [list of organizations]}
    """
    for ministry in clients.keys():
        for organization in clients[ministry]:
            page_info = [ministry, organization]
            downloads_pdf(driver, "ministry", page_info, oldest_date, 1, 99, key_words_list, authorized_approx, networkQualitySleepingTime, root, download_directory)
    print("ALL FINISHED ")
            


