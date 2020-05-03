import os.path
import threading
import queue
import sqlite3
from lib import *

def item_acquirer(item_ids, ready, flag, loop, threadnumber):
    con = sqlite3.connect(DATABASE_PATH)
    while not flag.is_set() and not ready.empty():
        ranges = ready.get()
        ids = ','.join(str(item) for item in item_ids[ranges[0]:ranges[1]])

        end = (item_ids[ranges[1]-1] if (ranges[1]-1 < len(item_ids)) else 'end')
        print(f'[{loop}:{threadnumber}] Acquiring ids {item_ids[ranges[0]]}-{end}...')
        items = get_object(ITEMS_LINK[0:-1] + '?ids=' + ids)

        if items is None:
            ready.put(ranges)
            flag.clear()
            continue

        items_tuples = []
        consumables_tuples = []
        for item in items:
            item_id = 0
            item_name = ''
            item_type = ''
            item_icon = ''
            details_type = ''
            details_description = ''
            details_duration_ms = 0
            details_apply_count = 1

            if 'id' in item:
                item_id = item['id']
            if 'name' in item:
                item_name = item['name']
            if 'type' in item:
                item_type = item['type']
            if 'icon' in item:
                item_icon = item['icon']
            if 'details' in item:
                d = item['details']
                if 'type' in d:
                    details_type = d['type']
                if 'description' in d:
                    details_description = d['description']
                if 'duration_ms' in d:
                    details_duration_ms = d['duration_ms']
                if 'apply_count' in d:
                    details_apply_count = d['apply_count']

            items_tuples.append((item_id, item_name, item_type, item_icon))
            if (item_type == 'Consumable' and (details_type == 'Food' or details_type == 'Utility')):
                consumables_tuples.append((item_id, item_name, details_type, details_description, details_duration_ms, details_apply_count))

        with con:
            c = con.cursor()
            c.executemany('insert into items values (?, ?, ?, ?)', items_tuples)
            c.executemany('insert into consumables values (?, ?, ?, ?, ?, ?)', consumables_tuples)

        if len(consumables_tuples) > 0:
            print(f'[{loop}:{threadnumber}] Got {len(consumables_tuples)} consumables.')

        if ready.empty():
            flag.set()
    con.close()

def run_item_acquirers(loop, item_ids):
    print(f'[{loop}] Acquiring items...')

    n = len(item_ids)
    ready = queue.Queue((n // 200) + 2)
    flag = threading.Event()
    for i in range(0, n, 200):
        ready.put((i, i+200))

    threads = []
    for i in range(MAX_THREADS):
        t = threading.Thread(target=item_acquirer, args=(item_ids, ready, flag, loop, i), daemon=True)
        threads.append(t)
        t.start()
        
    flag.wait()
    for t in threads:
        t.join()

def refresh_items_database():
    print('Refreshing items database...')
    con = sqlite3.connect(DATABASE_PATH)
    c = con.cursor()
    with con:
        c.execute(SQLITE_CREATE_ITEMS)
        c.execute(SQLITE_CREATE_CONSUMABLES)

    print('Starting data acquisition loop...')
    gettable = 1
    loop = 1
    while (gettable > 0):
        print(f'[{loop}] Getting items data from API...')
        item_ids = get_object(ITEMS_LINK)
        if item_ids is None:
            continue
        print(f'[{loop}] Excluding already available items...')
        with con:
            available = set()
            for thing in c.execute('select id from items'):
                available.add(int(thing[0]))
            item_ids = [x for x in item_ids if x not in available]
        gettable = len(item_ids)
        if (gettable > 0):
            run_item_acquirers(loop, item_ids)
            loop += 1

    with con:
        item_count = c.execute('select count(*) from items').fetchone()[0]
        consumables_count = c.execute('select count(*) from consumables').fetchone()[0]
    con.close()
    print(f'Confirmed {consumables_count} consumables out of {item_count} items.')
    