THREADS = []
MAX_THREADS = 5

SQLITE_CREATE_ITEMS = "create table if not exists items (id integer primary key, name text, type text)"
SQLITE_CREATE_CONSUMABLES = 'create table if not exists consumables (id integer primary key, name text, type text, description text, duration integer, apply_count integer)'
ITEMS_DATABASE_PATH = 'items.db'

API_BASE_LINK = 'https://api.guildwars2.com/v2/'
ITEMS_LINK = API_BASE_LINK + 'items/'
PRICES_LINK = API_BASE_LINK + 'commerce/prices/'
PRICES_LINK = API_BASE_LINK + 'commerce/listings/'