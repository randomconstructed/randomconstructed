import csv
import requests
import json

SET_LIST_URL = 'https://api.scryfall.com/sets'
SET_TYPE_WHITELIST = ['expansion', 'core']
SET_CODE_BLACKLIST = ['LEA', 'LEB', 'SUM', 'FBB', 'TSB']
SET_CSV_FILE = 'sets.csv'

def get_latest_set_list():
    r = requests.get(SET_LIST_URL).json()
    all_mtg_sets = r['data']
    whitelisted_sets = list(filter(lambda x:
                                   x['set_type'] in SET_TYPE_WHITELIST and
                                   x['code'].upper() not in SET_CODE_BLACKLIST,
                                   all_mtg_sets))
    whitelisted_sets.reverse()  # from oldest to newest
    return whitelisted_sets

def write_set_csv(set_list):
    with open(SET_CSV_FILE, 'w', newline='') as csvfile:
        writeCSV = csv.writer(csvfile, delimiter=',')
        csv_headers = ['Set No', 'Code', 'Name', 'Cards', 'URL']
        writeCSV.writerow(csv_headers)
        for i in range(0, len(set_list)):
            csv_row = [
                i,
                set_list[i]['code'].upper(),
                set_list[i]['name'],
                set_list[i]['card_count'],
                set_list[i]['scryfall_uri'],
            ]
            writeCSV.writerow(csv_row)

set_objects = get_latest_set_list()
write_set_csv(set_objects)

print('Saved ' + str(len(set_objects)) + ' sets in ' + SET_CSV_FILE)
