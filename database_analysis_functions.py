import pandas as pd
import os
from datetime import datetime
def read_gem_download_file(path, sheet_name = 'Sheet1'):
     
    df = pd.read_excel(path, sheet_name, header=0)
    if list(df.columns) != ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name","Downloaded", "Key word that filtered item"]:
        raise ValueError(f"Existing file {path} does not match template of columns:Download date, Ministry, Organisation, Bid's ID, Item name, Downloaded , Key word that filtered item")
    return df 



def read_multiple_gem_download_files(path_list, save_overall_df = False, saving_path = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\Gem_tenders_database"):
    overall_df = pd.DataFrame(columns = ["Download date", "Ministry", "Organisation", "Bid's ID", "Item name", "Downloaded", "Key word that filtered item"])
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
analysis download csv/database
"""

def get_clients_looked_up(df):
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

    print(f"In this database, {n_clients} clients  were looked up in {n_ministry} ministry: {clients.keys()}")
    print(f"There were {n_errors}, for clients in ministry {errors.keys()}")
    print(f"{len(df)} tenders were looked up")
    return f"In this database, {n_clients} clients  were looked up in {n_ministry} ministry: {clients.keys()}", f"There were {n_errors}, for clients in ministry {errors.keys()}", \
    f"{len(df)} tenders were looked up"


    


if __name__ == "__main__":
    dates_list = ["19-12-2023", "20-12-2023"]
    #path_list = generate_list_download_gem_path_from_dates(dates_list)
    #read_multiple_gem_download_files(path_list, save_overall_df=True)
    database_path = r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\Gem_tenders_database\MEETING - Gem_tenders_databaseGem database 22-12-2023.xlsx"
    df = read_gem_download_file(database_path, sheet_name = 'Feuil1' )
    database_report(df)