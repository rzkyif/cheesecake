import os.path
import threading
import queue
import sqlite3
from lib import *

def price_acquirer(item_ids, ready, flag, loop, threadnumber):
    con = sqlite3.connect(DATABASE_PATH)
    while not flag.is_set() and not ready.empty():
        ranges = ready.get()
        ids = ','.join(str(item) for item in item_ids[ranges[0]:ranges[1]])

        end = (item_ids[ranges[1]-1] if (ranges[1]-1 < len(item_ids)) else 'end')
        link = PRICES_LINK[0:-1] + '?ids=' + ids
        print(f'[{loop}:{threadnumber}] Acquiring prices for id {item_ids[ranges[0]]}-{end}...')
        prices = get_object(link)

        if prices is None:
            ready.put(ranges)
            flag.clear()
            continue

        prices_tuples = []
        for price in prices:
            item_id = 0
            item_whitelisted = 0
            price_buy = 0
            price_sell = 0

            if 'id' in price:
                item_id = price['id']
            if 'whitelisted' in price:
                item_whitelisted = 1 if price['whitelisted'] else 0
            if 'buys' in price:
                b = price['buys']
                if 'unit_price' in b:
                    price_buy = b['unit_price']
            if 'sells' in price:
                s = price['sells']
                if 'unit_price' in s:
                    price_sell = s['unit_price']

            prices_tuples.append((item_id, item_whitelisted, price_buy, price_sell))

        with con:
            c = con.cursor()
            c.executemany('insert into prices values (?, ?, ?, ?)', prices_tuples)

        if len(prices) > 0:
            print(f'[{loop}:{threadnumber}] Got {len(prices)} prices.')

        if ready.empty():
            flag.set()
    con.close()

def run_price_acquirers(loop, item_ids):
    print(f'[{loop}] Acquiring prices...')

    n = len(item_ids)
    ready = queue.Queue((n // 200) + 2)
    flag = threading.Event()
    for i in range(0, n, 200):
        ready.put((i, i+200))

    threads = []
    for i in range(MAX_THREADS):
        t = threading.Thread(target=price_acquirer, args=(item_ids, ready, flag, loop, i), daemon=True)
        threads.append(t)
        t.start()
        
    flag.wait()
    for t in threads:
        t.join()

def refresh_prices_database():
    print('Refreshing prices database...')
    con = sqlite3.connect(DATABASE_PATH)
    c = con.cursor()
    with con:
        c.execute(SQLITE_CREATE_PRICES)

    print('Starting data acquisition loop...')
    gettable = 1
    loop = 1
    while (gettable > 0):
        print(f'[{loop}] Getting item ids from database...')
        with con:
            item_ids = [r[0] for r in c.execute('select id from consumables').fetchall()]
        print(f'[{loop}] Picking only item ids in trading post...')
        tp_ids = set()
        prices = get_object(PRICES_LINK)
        if prices is None:
            continue
        for id in prices:
            tp_ids.add(id)
        item_ids = [x for x in item_ids if x in tp_ids]
        print(f'[{loop}] Excluding already available item ids...')
        with con:
            available = set()
            for thing in c.execute('select id from prices'):
                available.add(int(thing[0]))
            item_ids = [x for x in item_ids if x not in available]
        gettable = len(item_ids)
        if (gettable > 0):
            run_price_acquirers(loop, item_ids)
            loop += 1

    with con:
        prices_count = c.execute('select count(*) from prices').fetchone()[0]
    con.close()
    print(f'Acquired price information about {prices_count} items.')
    