import argparse
import calendar
import csv
import requests
from datetime import datetime, time, timedelta

# day of the week that new sets are generated (default Sunday)
GEN_DAY = calendar.SUNDAY
# time on the generation day to generate new sets (default 4pm)
GEN_HR = time(16)
DEFAULT_SETS_PATH = 'sets.csv'

parser = argparse.ArgumentParser()
parser.add_argument('--file', default=DEFAULT_SETS_PATH)

args = parser.parse_args()
csv_path = args.file


def get_last_gen_day():
    """Finds and returns the last day the codes were generated"""
    dt = datetime.utcnow()
    time = dt.time()
    date = dt.date()
    is_generation_day = date.weekday() == GEN_DAY and time >= GEN_HR
    if not is_generation_day:
        date -= timedelta(days=1)
    while date.weekday() != GEN_DAY:
        date -= timedelta(days=1)
    return date


def read_sets_csv(path):
    """Reads a CSV of sets, returns the set codes, names and number of sets"""
    # TODO: ensure CSV matches correct format
    set_codes = []
    set_names = []
    with open(path) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        next(readCSV)
        for row in readCSV:
            set_codes.append(row[1])
            set_names.append(row[2])
    num_sets = len(set_codes)
    return set_codes, set_names, num_sets


def get_block_hash(date):
    """Gets and returns the block has of the first block mined on the Bitcoin
    Cash blockchain after noon last generation day
    """
    h = None
    response = requests.get(
        'https://bch-chain.api.btc.com/v3/block/date/{}'.format(
            str(date).replace('-', '')
            )
        ).json()
    for block in reversed(response['data']):
        t = datetime.utcfromtimestamp(block['timestamp']).time()
        if t >= time(12):
            h = block['hash']
            break
    return h


def generate_set_indices(h, n):
    """Returns three numbers within number of set for use in selecting sets"""
    # pick the first set taking the last digit of the hash in base n
    x = int(h, 16)
    first = x % n-1
    # remove the last digit in base n
    x = int(x / n)

    # pick the second set taking the last digit of the previous step in base n-1
    second = x % (n-1)
    # this 'if' is the same as removing the first picked set from the list of sets
    if second >= first:
        second += 1
    # remove the last digit in base n-1
    x = int(x / (n-1))
    
    # pick the third set taking the last digit of the previous step in base n-2
    third = x % (n-2)
    # these 'ifs' are the same as removing the first and second picked sets from the list of sets
    if third >= min(first, second):
        third += 1
    if third >= max(first, second):
        third += 1
    return first, second, third


def get_set_codes_and_names():
    last_gen_day = get_last_gen_day()
    set_codes, set_names, num_sets = read_sets_csv(csv_path)
    print('Querying Bitcoin Cash blockchain to get random sets...')
    block_hash = get_block_hash(last_gen_day)
    first, second, third = generate_set_indices(block_hash, num_sets)

    # get the set codes of the picked sets
    codes = [set_codes[i] for i in [first, second, third]]
    names = [set_names[i] for i in [first, second, third]]
    return (codes, names)

codes, names = get_set_codes_and_names()

# print the link to view the cards allowed for this week (min 60 card deck, max 4 of each card)
print('The allowed sets are:\n', names)
print('You can view the pool of cards here:\nhttps://scryfall.com/search?order=usd&q=e%3A{}+or+e%3A{}+or+e%3A{}'.format(codes[0], codes[1], codes[2]))
