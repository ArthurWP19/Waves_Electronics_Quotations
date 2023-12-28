
from cgitb import lookup
import selenium 
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

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=C:\Users\arthu\AppData\Local\Google\Chrome\User Data\Profile 2") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome()
    return driver

def charging_web_page(driver, page_type,page_info):
    start_charging_time = time.time()
    driver.get('https://bidplus.gem.gov.in/advance-search')
    time.sleep(3)

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
    return(True)

def wait_until_all_tenders_charged(driver, last_page = False):
    """
    If last page, structure is different 
    """
    #WebDriverWait(driver, 60).until(lambda driver: len(driver.find_elements(By.XPATH, "//body//div[@class='card']")) > 1)  #supposes that if one tender is charged, all tenders of the page are - as it is observed
    #WebDriverWait(driver, 60).until(lambda driver: len(driver.find_elements(By.XPATH, "//div[@class='section-3']//a[@class='page-link']")) > 1)#we need also buttons, which are page-link, to be charged
    #we wait for tenders to be charged (class card), suppose that if one is charged, all ten are charged. We also wait for buttons to be charged: page links in section 3
    #WebDriverWait(driver, 60).until(lambda driver: len(driver.find_elements(By.XPATH, "(//div[@class='container'])[3]")) > 0)
    if last_page:
        WebDriverWait(driver, 120).until(lambda driver: len(driver.find_elements(By.XPATH, "//body//div[@class='card']"))) > 1 
    else: 
        WebDriverWait(driver, 120).until(lambda driver: len(driver.find_elements(By.XPATH, "//body//div[@class='card']")) > 1 
                                             and len(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[12]")) > 0)
    

def get_to_first_page(driver, first_page_number = 1):
     wait_until_all_tenders_charged(driver)
     last_page_number = int(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[6]")[0].text)
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


def filter_name(item_name, key_word_list = [], authorized_approx = 2):
    """
    returns a boolean, True if in key_word_list, False if not
    if key_word_list is empty, we don't filter
    authorized approx: number of differences authorized between item_name and key_words from list
    if there are words in item_name, if none of item_name word is in key_word list, we don't keep
    if item_name is only made of numbers and coma we keep for now

    """
    if key_word_list == []:
        return True
    

    else:
        numbers = []
        #parsing the item_name, using coma or space as separator
        parsed_item_name = re.split(r'[,\s]+', item_name)
        #delete Na elements if any
        parsed_item_name = [item for item in parsed_item_name if item]
        for word in parsed_item_name:
            #if word only made of float or int, means that it's not a word
            if re.match(r'^[+-]?\d+(\.\d+)?$', word):
                numbers.append(word)
            else:
                for key_word in key_word_list:
                        #we authorize two caracters gap 
                        if len(word) == len(key_word) and sum(c1 != c2 for c1, c2 in zip(word, key_word)) <= authorized_approx:
                            return True 
        #if only numbers in parsed_item_name, we'll download it to check item name in bid file       
        if len(numbers) == len(parsed_item_name):
            return True
        else:
            return False
                            
                    
   

def downloads_pdf(driver, page_type, page_info, oldest_date = "01-01-2000", first_page = 1, last_page = 99,  key_word_list = [], networkQualitySleepingTime = 3, root = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app",
                  download_directory = "C:/Users/arthu/Downloads"):
    """
    oldest date: expected string "dd-mm-aaaa": all tenders EMITTED AFTER emission date will be downloaded 
    first_page: no of the first page to look after research
    stop_page: no of the page to stop. stop_page should be superior to firs-page
    """
    if first_page > last_page:
        raise ValueError(f"First page input {first_page} shall not be superior to last page input {last_page}")
    
    organisation_name = page_info[1]
    # Initialisation of variable for files transfer
    now = time.strftime('%Y-%m-%d', time.localtime())
    
    folder_day= root +now+'/'
    if not os.path.exists(folder_day):
       os.makedirs(folder_day)
    intermediate_folder=root+now+'/'+organisation_name+'/'
    bin_folder=root +now+'/bin/'
    if not os.path.exists(intermediate_folder):
        os.makedirs(intermediate_folder)
    if not os.path.exists(bin_folder):
        os.makedirs(bin_folder)
    list_file=[]
    list_file_short_name=[] 
    compteur_bid=0
    #initializing driver and charging web page
    charging_web_page(driver, page_type, page_info)
    # going to the first page given as an input by the user 
    get_to_first_page(driver, first_page)
    # reading the last page available on Gem Website. If user input last_page > last_web_page, last_web_page is the final page 
    #TODO: solve this last page:
    if driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[7]")[0].text == "Next":
        last_web_page = int(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[6]")[0].text)
    else:
        last_web_page = int(driver.find_elements(By.XPATH, "/html/body/section[3]/div/div/div/div[13]/a[7]")[0].text)


    
    print("last web page", last_web_page)
    print("last page", last_page)
    if last_page > last_web_page:
        n_page_to_read = last_web_page - first_page
    else:
        n_page_to_read = last_page - first_page
    downloaded_bids = []
    for i in range(n_page_to_read+1):
        if i == n_page_to_read:
            last_page = True
        else: 
            last_page = False
        page_hyplist = []
        wait_until_all_tenders_charged(driver, last_page)
        #finding the number of tenders on page - usually it's ten, except for the last one
        n_tenders = len(driver.find_elements(By.CLASS_NAME, "card"))
        print("n_tenders on page", n_tenders)
        #Downloading all tenders if date superieur or equal to oldest_date 
        for n_tender in range (2,2 + n_tenders):
            #finding tender emission date on page
            starting_date_tender = driver.find_elements(By.XPATH, f'/html/body/section[3]/div/div/div/div[{n_tender}]/div[3]/div/div[3]/div[1]/span')[0]
            #reading emission date as a text
            starting_date_tender = starting_date_tender.text
            #keeping only dd-mm-aa
            starting_date_tender = starting_date_tender[0:10]
            starting_date_tender = datetime.strptime(starting_date_tender,  "%d-%m-%Y")
            oldest_date_tender = datetime.strptime(oldest_date,  "%d-%m-%Y")

            if starting_date_tender >= oldest_date_tender:

                #get name of bid on GeM website: only 7 number ID
                name_bid = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[{n_tender}]/div[1]/p[1]/a")[0].text[-7:]
                #GeM portal is having an issue : Sometimes, some tenders are put twice in the list on different pages
                #We keep track of the bids we already downloaded in downloaded_bids, so we don't click on them again
                print("**NAME_BID**", name_bid, downloaded_bids, "\\")
                if name_bid not in downloaded_bids: 
                    #get name of the file that is downloaded when we click on the bid - NOT THE SAME AS GEM BID NAME. ONLY 7 number ID
                    name_file = driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[{n_tender}]/div[1]/p[1]/a")[0].get_attribute("href")[-7:]
                    #dictionnary: key name of file, value: [bid_name, hyperlink]
                    page_hyplist.append({name_file: [name_bid, driver.find_elements(By.XPATH, f"/html/body/section[3]/div/div/div/div[{n_tender}]/div[1]/p[1]/a")[0]]})
                    downloaded_bids.append(name_bid)
                else:
                    print(f"Bid {name_bid} already downloaded")

        compteur_bid+=len(page_hyplist)
        
        print("DOWNLOADING")
        for file in page_hyplist:
            try :
                for file_name in file.keys():
                    #catch hyperlink 
                    elem = file[file_name][1]
                    elem.click()
                    wait_until_all_tenders_charged(driver, last_page)
            except NoSuchElementException :
                print(f"Erreur, bid {file_name} not clickable on page")
                continue
        #Renaming files with GeM: bid name 

        #first wait for all files to be downloaded - allow several trials 
        time.sleep(4)
        n_attempt = 0
        print("downloaded bids", downloaded_bids)
        print("RENAMING FILES")
        for n_attempt in range(11):
            if n_attempt == 10:
                raise Exception("All files not downloaded after 10 attempts ")
            try: 
                #if try to rename a file that was already renamed in previous attempt, error 
                renamed_files = []   
                for file in page_hyplist:
                    for file_name in file.keys():
                        downloaded_file_name = os.path.join(download_directory, f"GeM-Bidding-{file_name}.pdf")
                        bid_name = os.path.join(download_directory, f"GeM-Bidding-{file[file_name][0]}.pdf")
                        os.rename(downloaded_file_name, bid_name)
                        renamed_files.append(file)
                        print(f"file {file_name} as been renamed to {file[file_name][0]}")
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
        if i < n_page_to_read:
            next_button=driver.find_element(By.XPATH,'//*[@class="page-link next"]')
            next_button.click()
    
    print("FINISHED")
    return list_file

def test_charging_web_page():
    driver = get_driver()
    charging_web_page(driver, "ministry", ["MINISTRY OF DEFENCE", "GOA SHIPYARD LIMITED"])

def test_downloads_pdf():
    driver = get_driver()
    downloads_pdf(driver, "ministry",["MINISTRY OF DEFENCE", "GOA SHIPYARD LIMITED"], oldest_date= "22-11-2023", first_page=1, last_page=1, key_word_list = ["Rhino"])
    print("successful")


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
if __name__ == "__main__":
    test_downloads_pdf()