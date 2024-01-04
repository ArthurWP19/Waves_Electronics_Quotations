import PySimpleGUI as sg
from Functions_clients_database import read_clients_name
from Functions_web_page import download_multiple_pdf, get_driver
from Functions_interface import set_departments_window, set_ministry_window, run_ministry_window, set_display_selection_window, run_display_selection_window, run_search_result_window, set_search_result_window
from Functions_interface import set_download_results_window, run_download_results_window
sg.theme('LightGrey1')  # Theme selection
from datetime import datetime
from Tenders_database_analysis_functions import generate_download_gem_path_from_date
# Votre dictionnaire de clients
clients_database = read_clients_name(r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\clients_database")
import re 

# Titre et sous-titres pour les sections
title_font = ('Helvetica', 24, 'bold')
subtitle_font = ('Helvetica', 18, 'underline')
background_color = '#f0f0f0'  # Couleur d'arrière-plan gris clair
text_color = '#333333'  # Couleur de texte gris foncé

layout = [
    [sg.Text('Downloading Tenders', font=title_font, justification='center', size=(30, 1), text_color=text_color)],
    [sg.Text('Client Selection', font=subtitle_font, pad=((0, 10), (20, 5)), text_color=text_color)],
    [sg.Text('Search with checkboxes', text_color=text_color), sg.Button('Search', key="-SEARCH WITH CHECKBOXES-", size=(15, 1))],
    [sg.Text('Search with organization name', text_color=text_color), sg.Button("Search", key="-SEARCH-", size=(30, 1))],
    [sg.InputText(key="-SEARCHED EXPRESSION-", size=(30, 1))],
    [sg.Text('Display currently selected clients', text_color=text_color), sg.Button('Display current selected clients', key="-DISPLAY CURRENT CLIENTS SELECTION-", size=(30, 1))],
    [sg.Text('Research Parameters', font=subtitle_font, pad=((0, 20), (20, 5)), text_color=text_color)],
    
    [sg.Text('Key Words', size=(15, 1), text_color=text_color), sg.InputText(key="-KEY WORDS-", size=(50,60), expand_y = True)],
    [sg.Text('Download', font=subtitle_font, pad=((0, 20), (20, 5)), text_color=text_color)],
    [sg.Button('Download', key="-DOWNLOAD-", size=(15, 1))]
]
#[sg.Text('Oldest Date', size=(15, 1), text_color=text_color), sg.InputText(key="-OLDEST_DATE-", size=(30, 1))]
window = sg.Window('Main Window', layout, background_color=background_color)
selected_clients = {}
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "-SEARCH WITH CHECKBOXES-":
        ministry_window = set_ministry_window(clients_database)
        #add newly selected clients from ministry window, to previously selected clients 
        selected_clients = run_ministry_window(ministry_window, clients_database, selected_clients)
        print(selected_clients)
    elif event == "-SEARCH-":
        searched_expression = values["-SEARCHED EXPRESSION-"]
        search_result_window = set_search_result_window(searched_expression, clients_database, selected_clients)
        selected_clients = run_search_result_window(search_result_window, clients_database, selected_clients)
        print(selected_clients)
    elif event == "-DISPLAY CURRENT CLIENTS SELECTION-":
        selection_window = set_display_selection_window(selected_clients)
        run_display_selection_window(selection_window)
    elif event == "-DOWNLOAD-":

        #set download function
        #oldest_date = values["-OLDEST_DATE-"]
        oldest_date = "01-01-2000"
        read_key_word_list = values["-KEY WORDS-"]
        parsed_key_word_list = re.split(r'\s*,\s*', read_key_word_list)
        key_word_list = [key_word for key_word in parsed_key_word_list]
    

        if oldest_date == None:
            oldest_date = "01-01-2000"
        if key_word_list == None:
            key_word_list = []


        root = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app"
        download_dir = "C:/Users/arthu/Downloads"
        driver = get_driver()
        print("selected clients", selected_clients)
        download_multiple_pdf(driver, clients = selected_clients, oldest_date=oldest_date, key_words_list=key_word_list, authorized_approx=2, networkQualitySleepingTime=3, \
                              root = root, download_directory=download_dir)
        today_date = datetime.now().strftime("%d-%m-%Y")
        download_file_path = generate_download_gem_path_from_date(today_date, root)
        download_results_window = set_download_results_window(download_file_path)
        run_download_results_window(download_results_window)

 
window.close()


