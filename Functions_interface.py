import re
import select
from symbol import break_stmt
import PySimpleGUI as sg

sg.theme('LightGrey1')  # Theme selection
from Tenders_database_analysis_functions import read_gem_download_file, database_report

"""
TOOLS
"""
def get_center_coordinate_for_window(window_width = 1000, window_height = 300):
        screen_width, screen_height = sg.Window.get_screen_size()
        left_margin = (screen_width - window_width) // 2
        top_margin = (screen_height - window_height) // 2
        return (left_margin, top_margin)

def parse_key_word_input(key_word_list):
        """
        expects an input as given by GUI interface: "word1, word2,...,"
        """
        list_key_words = []
        parsed_key_word_list = re.split(r'[, \t_\-]+', key_word_list)
        #delete Na elements if any
        parsed_key_word_list = [word for word in parsed_key_word_list if word]
        for word in parsed_key_word_list:
                list_key_words.append(word)
        return list_key_words

def search_function(searched_expression, clients_database):
       
       """
       we are looking for all organizations in clients_database which contain search expression
       return a dictionnary {ministry: organization:list }
       """
       results = {}
       ministry_to_del = []
       for ministry in clients_database.keys():
                results[ministry] = []
                for organization in clients_database[ministry]:
                        if searched_expression.lower() in organization.lower():
                                print("organization", organization)
                                results[ministry].append(organization)
                if results[ministry] == []:
                       ministry_to_del.append(ministry)
       for min in ministry_to_del:
              del results[min]
       
       return results
def get_ministry_from_department(department, clients_database):
       for ministry in clients_database.keys():
              if department in clients_database[ministry]:
                     return ministry
       raise Exception(f"department {department} not found in client database")
       
                            
"""
SETTING WINDOWS
"""

def set_ministry_window(clients_database):
        # Creating the interface layout with scrolling
        ministry_layout = [
        [sg.Text("Select the ministry:")],
        [sg.Button("Exit", key ="-SELECTION EXIT-")],
        [sg.Listbox(values=list(clients_database.keys()), size=(300, 35), key="-DEPARTMENTS SELECTION-", enable_events=True)],
        [sg.Button("Exit", key ="-SELECTION EXIT-")]
        ]
        ministry_window = sg.Window("Ministry/Department Selection", ministry_layout, size=(1000, 400))
        return ministry_window

def set_departments_window(clients_database, selected_ministry_name, previously_selected_departments):

        ministry_departments = clients_database[selected_ministry_name]
        departments_col = []
        #if department in previously selected department, pre check the check box
        for department in ministry_departments:
                if department in previously_selected_departments:
                        departments_col.append([sg.Checkbox(department, default=True, key=department)])
                else:
                        departments_col.append([sg.Checkbox(department, default=False, key=department)])
        #if no department for this ministry, we have to manually add an empty least to avoid issues
        if len(departments_col) == 0:
               departments_col = [[]]

        checkboxes_layout = [
                [sg.Button("Select all", font=("Helvetica", 10, "bold"), key="-SELECT ALL-")],
                [sg.Button("Deselect all", font=("Helvetica", 10, "bold"), key="-DESELECT ALL-")],
                [sg.Column(departments_col, size=(1000,300), scrollable=True)],
                [sg.Button("Confirm", key = "-DEPARTMENTS SELECTION CONFIRM-")]
                ]

        department_window_location = get_center_coordinate_for_window()
        departments_window = sg.Window(f"Departments for {selected_ministry_name}",checkboxes_layout, finalize=True, location=department_window_location)
        return departments_window

def set_display_selection_window(selected_clients):
        clients_layout = [[sg.Text("Currently selected clients")]]
        if selected_clients == {}:
               clients_col = [[]]
        else: 
                clients_col = []
                for ministry in selected_clients.keys():
                        clients_col.append([sg.Text(ministry, font=('Helvetica', 12, 'bold'))])
                        for department in selected_clients[ministry]:
                                clients_col.append([sg.Text(department)])
        print(clients_col)

        clients_layout.append([sg.Column(clients_col, size=(1000,300), scrollable=True)])
        clients_layout.append([sg.Button("Exit", key ="-EXIT-")])
        print(clients_layout)
        display_selection_window = sg.Window("Ministry/Department Selection", clients_layout, size=(1000, 400))
        return display_selection_window


       
       
def set_search_result_window(searched_expression, clients_database, previously_selected_clients):
        layout = [[sg.Text(f"Results of search in clients database for expression: {searched_expression}", font=('Helvetica', 12, 'bold'), key = "-TITLE-")]
                        ]
        results = search_function(searched_expression, clients_database)
        results_layout = []
        if results == {}:
                results_col = [[]]
        else: 
                results_col = []
                for ministry in results.keys():
                        results_col.append([sg.Text(ministry, font=('Helvetica', 12, 'bold'), key = "-title-")])
                        for department in results[ministry]:
                                #if department already previously selected, check it 
                                default_check = False
                                if ministry in previously_selected_clients.keys():
                                       if department in previously_selected_clients[ministry]:
                                                default_check = True
                                results_col.append([sg.Checkbox(department, default=default_check, key=department)])

        results_layout.append([sg.Column(results_col, size=(1000,300), scrollable=True)])
        results_layout.append([sg.Button("Confirm", key = "-ORGANIZATION SELECTION CONFIRM-")])
        search_result_window = sg.Window("Ministry/Department Selection", results_layout, size=(1000, 400))
        return search_result_window


def set_download_results_window(download_file_path):
       
       df_downloads = read_gem_download_file(download_file_path)
       report = database_report(df_downloads)
       n_clients = report[0]
       n_ministry = report[1]
       n_errors = report[2]
       n_tenders = report[3]
       layout = [[sg.Text(f"Downloading finished", font=('Helvetica', 14, 'bold'), key = "-TITLE-"), sg.Text(f" WARNING: figures below include all downloads of the day", font=('Helvetica', 14, 'italic'), key = "-TITLE-")],
                [sg.Text(f"{n_clients} clients were looked in {n_ministry} ministry ", font=('Helvetica', 12), key = "-TITLE-")],
                [sg.Text(f"{n_tenders} tenders were looked up", font=('Helvetica', 12,), key = "-TITLE-")], 
                [sg.Text(f"{n_errors} errors occured - see in download file", font=('Helvetica', 12), key = "-TITLE-")]
                ]
       download_results_window = sg.Window("Download results", layout , size=(1000, 400))
       return download_results_window


       
      
       


"""
RUNNING WINDOWS
"""
def run_departments_window(departments_window):
      while True:
                
                event, values = departments_window.read()
                if event == "-SELECT ALL-":
                        
                        for key in values:
                                if key not in ["-SELECT ALL-", "-DESELECT ALL-", "-CONFIRM-"]:
                                        departments_window[key].update(value = True)
                elif event == "-DESELECT ALL-":
                        for key in values:
                                if key not in ["-SELECT ALL-", "-DESELECT ALL-", "-CONFIRM-"]:
                                        departments_window[key].update(value = False)
                elif event == "-DEPARTMENTS SELECTION CONFIRM-":
                        selected_departments = []
                        #not_selected_departments = []
                        for key in values:
                                if key not in ["-SELECT ALL-", "-DESELECT ALL-", "-CONFIRM-"]:
                                #if checkbox is checked 
                                        if departments_window[key].get() == True:
                                                selected_departments.append(key)
                                        #elif departments_window[key].get() == False:
                                                #not_selected_departments.append(key)
                                               
                                                
                        departments_window.close()
                        return selected_departments
                elif event == sg.WINDOW_CLOSED:
                        departments_window.close()
                        break
                        
                
      
     
def run_ministry_window(ministry_window, clients_database, selected_clients):
        intermediate_selected_clients = {}
        while True:
            event, values = ministry_window.read()
            if event == sg.WINDOW_CLOSED:
                #if window closed, we return previsous selected_clients_dict
                ministry_window.close()
                return selected_clients
            
            elif event == "-DEPARTMENTS SELECTION-":
                selected_ministry_name= values["-DEPARTMENTS SELECTION-"][0]
                #check if for the selected ministry, we already selected departments; If yes, we will pre-check them in window department
                if selected_clients is not None and selected_ministry_name in selected_clients.keys():
                        previously_selected_departments = selected_clients[selected_ministry_name]
                else:
                       previously_selected_departments = []
                departments_window = set_departments_window(clients_database, selected_ministry_name, previously_selected_departments)
                selected_departments = run_departments_window(departments_window)
                #if we selected at least one depattment for the ministry
                if selected_departments is not None and selected_departments != []:
                       intermediate_selected_clients[selected_ministry_name] = selected_departments
                #Once department window is opened
            elif event == "-SELECTION EXIT-":
                #update selected_clients_dict. Erase previous selection for a ministry, if new selection
                for ministry in intermediate_selected_clients:
                       selected_clients[ministry] = intermediate_selected_clients[ministry]
                ministry_window.close()
                return selected_clients
                
               
                
def run_display_selection_window(display_selection_window):
       while True:
            event, values = display_selection_window.read()
            if event == sg.WINDOW_CLOSED:
                display_selection_window.close()
                break
            elif event == "-EXIT-":
                display_selection_window.close()
                break
        
            
def run_search_result_window(search_result_window, clients_database, selected_clients):
       intermediate_selected_clients = {}
       while True: 
        event, values = search_result_window.read()
        if event == sg.WINDOW_CLOSED:
                search_result_window.close()
                return {}
        elif event == "-ORGANIZATION SELECTION CONFIRM-":
                #read checked departments on window
                selected_departments = []
                for department in values:
                        if department not in ["-TITLE-", "-title-", "-ORGANIZATION SELECTION CONFIRM-"]:
                        #if checkbox is checked 
                                if search_result_window[department].get() == True:
                                        selected_departments.append(department)
                #find corresponding ministry, assemble intermediate_selected_clients dictionnary
                for department in selected_departments:
                       ministry = get_ministry_from_department(department, clients_database)
                       if ministry not in intermediate_selected_clients.keys():
                              intermediate_selected_clients[ministry] = [department]
                       else:
                              intermediate_selected_clients[ministry].append(department)
                #update selected_clients_dict. Erase previous selection for a ministry, if new selection
                for ministry in intermediate_selected_clients:
                       selected_clients[ministry] = intermediate_selected_clients[ministry]
                search_result_window.close()
                print("selected clients after checking")
                return selected_clients
        

                
def run_download_results_window(download_results_window):
       while True:
            event, values = download_results_window.read()
            if event == sg.WINDOW_CLOSED:
                download_results_window.close()
                break
            elif event == "-EXIT-":
                download_results_window.close()
                break
               
              
       