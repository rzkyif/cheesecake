import urllib.request
import os
from urllib.error import URLError
from socket import timeout
from json import load, loads, JSONDecodeError
from http.client import IncompleteRead

VERSION = '1.0.0'
REFRESH = False

STAT_NAMES = [
    'Power',
    'Precision',
    'Ferocity',
    'Toughness',
    'Vitality',
    'Concentration',
    'Condition Damage',
    'Expertise',
    'Healing Power',
    'Magic Find',
    'Experience (gained)',
    'Experience (from kills)'
]
STAT_LOOKUP = [
    ' Power',
    ' Precision',
    ' Ferocity',
    ' Toughness',
    ' Vitality',
    ' Concentration',
    ' Condition Damage',
    ' Expertise',
    ' Healing Power',
    '% Magic Find',
    '% All Experience Gained',
    '% Experience from kills)'
]

THREADS = []
MAX_THREADS = 7

SQLITE_CREATE_ITEMS = "create table if not exists items (id integer primary key, type text, icon text)"
SQLITE_CREATE_CONSUMABLES = 'create table if not exists consumables (id integer primary key, name text, type text, description text, duration integer, apply_count integer, level integer)'
SQLITE_CREATE_PRICES = "create table if not exists prices (id integer primary key, whitelisted integer, price_buy integer, price_sell integer)"
DATABASE_PATH = 'cheesecake.db'

API_BASE_LINK = 'https://api.guildwars2.com/v2/'
ITEMS_LINK = API_BASE_LINK + 'items/'
PRICES_LINK = API_BASE_LINK + 'commerce/prices/'

def get_object(url):
    try:
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = load(response)
                return data
        except IncompleteRead as e:
            try:
                data = loads(e.partial.read().decode())
            except JSONDecodeError as jde:
                print('GET: IncompleteRead: JSONDecodeError: Partial read decode error!')
                return None
            else:
                return data
        except URLError as e:
            print('GET: URLError: ' + str(e))
            return None
        except timeout as e:
            print('GET: timeout: ' + str(e))
            return None
    except e:
        print('GET: Error: ' + str(e))
        return None

def moneytalk(copper):
    s = ''
    silver = copper // 100
    gold = silver // 100
    silver = silver % 100
    copper = copper % 100
    if gold > 0:
        s += str(gold)
        s += ' gold '
    if silver > 0:
        s += str(silver)
        s += ' silver '
    if copper > 0:
        s += str(copper)
        s += ' copper'
    return s

def clear(): 
    if os.name == 'nt': 
        _ = os.system('cls') 
    else: 
        _ = os.system('clear') 