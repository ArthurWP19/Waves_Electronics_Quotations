import pandas as pd
import os
from Functions_clients_database import read_clients_name
from datetime import datetime

"""
Reading functions 
"""

def read_gem_download_file(path, sheet_name = 'Sheet1'):
    """
    Returns the dataframe corresponding to an excel list of downloads
    """
     
    df = pd.read_excel(path, sheet_name, header=0)
    if list(df.columns) != ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name","Downloaded", "Key word that filtered item", "Starting date", "End date"]:
        raise ValueError(f"Existing file {path} does not match template of columns:Download date, Ministry, Organisation, Bid's ID, Item name, Downloaded , Key word that filtered item", "Starting date", "End date")
    return df 



def read_multiple_gem_download_files(path_list, save_overall_df = False, saving_path = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\Gem_tenders_database"):
    """
    Concatenate several excels of downloads in one database
    """
    overall_df = pd.DataFrame(columns = ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name", "Downloaded", "Key word that filtered item", "Starting date", "End date"])
    for path in path_list:
        df = read_gem_download_file(path)
        overall_df = pd.concat([overall_df, df]).reset_index(drop=True)
    if save_overall_df:
        today_date = datetime.now().strftime("%d-%m-%Y")
        file_name = f"Gem database {today_date}.xlsx"
        file_path= saving_path + file_name
        overall_df.to_excel(file_path, index=False, header = True)
    return overall_df

def generate_download_gem_path_from_date(date, root = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app"):
    """
    From a date and a root, generate the download list path, if it exits 
    """
    path = root + f"/Downloads GEM {date}/{date} - GeM downloads.xlsx"
    print("path", path)
    if os.path.exists(path):
        return path
    else:
        print(f"Download Gem folder does not exist for date {date} in root folder {root}")
        return None

def generate_list_download_gem_path_from_dates(dates_list, root = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app"):
    path_list = []
    for date in dates_list:
        path = generate_download_gem_path_from_date(date, root)
        if path is not None:
            path_list.append(path)
    return path_list 

"""
Analysis of excel downloads files 
"""

def get_clients_looked_up(df):
    """
    Returns a dictionnary {ministry: client} with all clients looked up in dataframe
    """
    clients_looked_up = {}
    ministry_looked_up = []
    organizations_looked_up = []
    for index, row in df.iterrows():
        organization = row["Organisation"]
        if organization not in organizations_looked_up:
            organizations_looked_up.append(organization)
            ministry = row["Ministry"]
            if ministry not in ministry_looked_up:
                ministry_looked_up.append(ministry)
                clients_looked_up[ministry] = []
            clients_looked_up[ministry].append(organization)
    return clients_looked_up

def get_clients_errors(df):
    """
    Returns a dictionnary {ministry : clients} of all clients where an error was encontered in download 
    """
    clients_looked_up_with_error = {}
    ministry_looked_up = []
    organizations_looked_up = []
    for index, row in df.iterrows():
        organization = row["Organisation"]
        if organization not in organizations_looked_up:
            if isinstance(row["Bid's ID"], str) and "error" in row["Bid's ID"].lower():
                organizations_looked_up.append(organization)
                ministry = row["Ministry"]
                if ministry not in ministry_looked_up:
                    ministry_looked_up.append(ministry)
                    clients_looked_up_with_error[ministry] = []
                clients_looked_up_with_error[ministry].append(organization)
    
    return clients_looked_up_with_error


def database_report(df):
    clients = get_clients_looked_up(df)
    n_ministry = len(clients.keys())
    n_clients = 0
    for ministry in clients.keys():
        n_clients += len(clients[ministry])
    

    errors = get_clients_errors(df)
    n_errors = 0
    for ministry in errors.keys():
        n_errors += len(errors[ministry])

    print(f"In this database, {n_clients} clients  were looked up in {n_ministry} ministry")
    print(f"There were {n_errors} errors, for clients in ministry {errors.keys()}")
    print(f"{len(df)} tenders were looked up")
    return f"In this database, {n_clients} clients  were looked up in {n_ministry} ministry: {clients.keys()}", f"There were {n_errors}, for clients in ministry {errors.keys()}", \
    f"{len(df)} tenders were looked up"

def count_clients(dict_clients):

    n_clients = 0
    for ministry in dict_clients:
        n_clients += len(dict_clients[ministry])
    return n_clients
    
def find_missing_clients_in_database(df):
    """
    Returns a dictionnary {ministry: organization} with organizations that are in clients database, but not looked up in the excel 
    """
    clients_database = read_clients_name(r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\clients_database")
    missing_clients = {}
    clients_looked_up = get_clients_looked_up(df)
    for ministry in clients_database.keys():
        if ministry not in clients_looked_up.keys():
            print("ministry not in client_looked_up", ministry)
            missing_clients[ministry] = clients_database[ministry]
        else:
            for organization in clients_database[ministry]:
                if organization not in clients_looked_up[ministry]:
                    print("organization not looked up", organization)
                    if ministry in missing_clients.keys():
                        missing_clients[ministry].append(organization)
                    else:
                        missing_clients[ministry] = [organization]
    looked_missing = {}
    for ministry in clients_database:
        if ministry in clients_looked_up.keys():
            looked_missing[ministry] = clients_looked_up[ministry]
        else:
            looked_missing[ministry] = missing_clients[ministry]
    for ministry in clients_database.keys():
    
        print(ministry, "looked_up_missing", len(looked_missing[ministry]), "database", len(clients_database[ministry]))
    return missing_clients



"""
Manipuating excel downloads files 
"""


def complete_main_database(path_database, path_df_downloads):
    """
    Main database is an excel. 
    Looks up in a new daily download excel file, adds tenders in the main database, if they are not already there. 
    if bid name is not in database, or if data not found, adds to database
    if error, does not add 
    """
    df_database = read_gem_download_file(path_database)
    list_bid_names_database = df_database["Bid's ID"].tolist()
    print(list_bid_names_database)
    df_downloads = read_gem_download_file(path_df_downloads)
    for index, row in df_downloads.iterrows():
        bid_id = row["Bid's ID"]
        if bid_id == "NO DATA FOUND ON GEM WEBSITE":
            df_database.loc[len(df_database)] = row
        elif isinstance(row["Bid's ID"], str) and "error" in row["Bid's ID"].lower():
            pass
        else:
            if bid_id not in list_bid_names_database:
                df_database.loc[len(df_database)] = row
            else:
                print(bid_id)
    file_path_new = path_database[:-5] + "_completed.xlsx"
    df_database.to_excel(file_path_new, index=False, header = True)
    print(f"Database {path_database} completed with file {path_df_downloads}")
    return 
            

    
