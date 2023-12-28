from Functions_web_page import filter_name, convert_lowercase
from Gem_clients import read_clients_name


string_test = "battery charger, tulipe"
string_test_2 = "rectifier, jean"
string_test_3 = "battery 6 charging modules"
string_test_4 = "PR_ 100228096_ M9244921263_ BATTERY RECHARGEABLE_ Schedule-1,PR_ 100228096_ M9208240032_ BATTERY, R"

key_words = ["battery charger", "battery charging", "charging modules",  "transrectifier", "DC_UPS", "inverter", "FCBC charger", "Battery accessories", "Battery charg"]

for c,d in zip("charger", "gear"):
    print(c,d)
clients_database = read_clients_name(r"C:\Waves Electronics 2023-2024 - programming\Quotations\Srapping tenders\New app\clients")
for client in clients_database.keys():
    if client == "MINISTRY OF POWER":
        print(clients_database[client])
