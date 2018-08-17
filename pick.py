import pandas
import requests
from datetime import datetime, time, date, timedelta
import calendar

# find the last Sunday (this Sunday if the time is after 4 and today is Sunday)
dt = datetime.utcnow()
t = dt.time()
d = dt.date()
if not(d.weekday() == calendar.SUNDAY and t >= time(16)):
    d -= timedelta(days=1)
while d.weekday() != calendar.SUNDAY:
    d -= timedelta(days=1)
last_sunday = d

# read in the list of mtg sets
sets = pandas.read_csv('sets.csv')
n = len(sets)

# get the block hash of the first block mined on the Bitcoin Cash blockchain after noon last Sunday
h = None
r = requests.get('https://bch-chain.api.btc.com/v3/block/date/{}'.format(str(last_sunday).replace('-', ''))).json()
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
selected = sets[sets['Set No'].isin([first, second, third])]
print(selected)
c = list(selected['Code'])

# print the link to view the cards allowed for this week (min 60 card deck, max 4 of each card)
print('https://scryfall.com/search?order=color&q=e%3A{}+or+e%3A{}+or+e%3A{}'.format(c[0], c[1], c[2]))