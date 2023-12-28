import PySimpleGUI as sg
from Functions_web_page import get_driver, charging_web_page, downloads_pdf
from Functions_interface import parse_key_word_input
sg.theme('LightGrey1')  # Theme selection



# Dropdown options for the Ministry selection
ministry_options = ['Ministry of Defence', 'Ministry of Coal']
access_web_page_layout = [
    [sg.Text('Access Web Page', size=(20, 1), font=('Helvetica', 20), justification='center')],
    [sg.Text('Ministry:', size=(10, 1)), sg.Combo(ministry_options, default_value='Ministry of Defence', key='ministry')],
    [sg.Text('Organisation:', size=(10, 1)), sg.InputText(default_text='GOA SHIPYARD LIMITED', key='organization')],
    [sg.Text('Access Web Page', size=(20, 1), font=('Helvetica', 20), justification='center')],
    [sg.Text('Ministry:', size=(10, 1)), sg.InputText(default_text='MINISTRY OF DEFENCE', key='ministry')],
    [sg.Text('Organisation:', size=(10, 1)), sg.InputText(default_text='GOA SHIPYARD LIMITED', key='organization')],
    [sg.Button('Access', size=(10, 2), font=('Helvetica', 15)), 
     sg.Button('Close', size=(10, 2), font=('Helvetica', 15)), 
     sg.Text('', size=(30, 1), key='status')],
]

download_tenders_layout = [
    [sg.Text('Download Tenders', size=(20, 1), font=('Helvetica', 20), justification='center')],
    [sg.Text('Arthur', size=(20, 1))],  # Explanation text - to be filled later
    [sg.Text('First Page:', size=(10, 1)), sg.InputText(key='first_page')],
    [sg.Text('Last Page:', size=(10, 1)), sg.InputText(key='last_page')],
    [sg.Text('Oldest Date:', size=(10, 1)), sg.InputText(key='oldest_date')],
    [sg.Text('Key words', size=(10, 1)), sg.InputText(key='key_word_list')],
    [sg.Button('Download', size=(10, 2), font=('Helvetica', 15))],

]

layout = [
    [sg.Column(access_web_page_layout, element_justification='c')],
    [sg.Column(download_tenders_layout, element_justification='c')],
]

window = sg.Window('Application Name', layout, size=(600, 600))

page_open = False

while True:
    event, values = window.read()
    ministry = values['ministry']
    organisation = values['organization']
    first_page = int(values['first_page'])
    last_page = int(values['last_page'])
    oldest_date = values['oldest_date']
    key_word_list = parse_key_word_input(values["key_word_list"])
    
    driver = get_driver()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Access':
        window['status'].update('Access in progress...', text_color='black')

        try:
            charging_web_page(driver, "ministry", [ministry, organisation])
            window['status'].update('Execution successful!', text_color='black')
        except Exception as e:
            print(f"An error occurred: {e}")
            window['status'].update('An error occurred', text_color='red')
    
    if event == 'Download':
        # Call download_pdf function with parameters from input fields


        try:
            window['status'].update("Download in process...", text_color='black')
            downloads_pdf(driver, "ministry", [ministry, organisation], oldest_date, first_page, last_page, key_word_list)  # Assuming download_pdf takes these parameters
            window['status'].update('PDF Downloaded!', text_color='black')
        except Exception as e:
            print(f"An error occurred while downloading PDF: {e}")
            window['status'].update('Error downloading PDF', text_color='red')


    if event == 'Close':
        page_open = False
        window.hide()

    window.finalize()

    if not page_open:
        break

window.close()
