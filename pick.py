# day of the week that new sets are generated (default Sunday)
import calendar
GENDAY = calendar.SUNDAY

import csv
import requests
from datetime import datetime, time, timedelta

print('Querying Bitcoin Cash blockchain to get random sets...')

# find the last generation day (today if the time is after 4 and today is the generation day)
dt = datetime.utcnow()
t = dt.time()
d = dt.date()
if not(d.weekday() == GENDAY and t >= time(16)):
    d -= timedelta(days=1)
while d.weekday() != GENDAY:
    d -= timedelta(days=1)
last_genday = d

# read in the list of mtg sets
set_codes = []
set_names = []
with open('sets.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    next(readCSV)
    for row in readCSV:
        set_codes.append(row[1])
        set_names.append(row[2])
n = len(set_codes)

# get the block hash of the first block mined on the Bitcoin Cash blockchain after noon last generation day
h = None
r = requests.get('https://bch-chain.api.btc.com/v3/block/date/{}'.format(str(last_genday).replace('-', ''))).json()
for block in reversed(r['data']):
    t = datetime.utcfromtimestamp(block['timestamp']).time()
    if t >= time(12):
        h = block['hash']
        break

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

# get the set codes of the picked sets
codes = [set_codes[i] for i in [first, second, third]]
names = [set_names[i] for i in [first, second, third]]

# print the link to view the cards allowed for this week (min 60 card deck, max 4 of each card)
print('The allowed sets are:\n', names)
print('You can view the pool of cards here:\nhttps://scryfall.com/search?order=usd&q=e%3A{}+or+e%3A{}+or+e%3A{}'.format(codes[0], codes[1], codes[2]))
