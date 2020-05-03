import urllib.request
from urllib.error import URLError
from socket import timeout
from json import load, loads, JSONDecodeError
from http.client import IncompleteRead

THREADS = []
MAX_THREADS = 7

SQLITE_CREATE_ITEMS = "create table if not exists items (id integer primary key, name text, type text, icon text)"
SQLITE_CREATE_CONSUMABLES = 'create table if not exists consumables (id integer primary key, name text, type text, description text, duration integer, apply_count integer)'
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
        print('error: ' + str(e))
        return None