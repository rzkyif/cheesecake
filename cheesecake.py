import items
import prices
import sqlite3
import re
from lib import *

def f(c, r, v, k, x):
    if k == 0:
        p = [([id], r[k][id]) for id in v[k] if c[k][id] <= x]
    else:
        p = []
        for id in v[k]:
            if c[k][id] > x:
                continue
            ids, previous_f = f(c, r, v, k-1, x-c[k][id])
            ids.append(id)
            p.append((ids, r[k][id] + previous_f))
    max_id = max(range(len(p)), key=lambda x: p[x][1])
    return p[max_id]

if __name__ == "__main__":
    if REFRESH:
        items.refresh_items_database()
        prices.refresh_prices_database()
    
    con = sqlite3.connect(DATABASE_PATH)
    c = con.cursor()

    clear()
    print('Cheesecake ' + VERSION + '\n')
    input_level = int(input('Enter character level: '))
    
    clear()
    print('Cheesecake ' + VERSION + '\n')
    input_budget = int(input('Enter budget (in copper coins): '))

    clear()
    print('Cheesecake ' + VERSION + '\n')
    input_instant = input('Use instant buy price? (Y/n): ').lower() != 'n'

    clear()
    print('Cheesecake ' + VERSION + '\n')
    print('Status list:')
    for i, name in enumerate(STAT_NAMES):
        print(f'({i+1}) {name}')
    input_stats = input('Enter id(s) of stat(s) to find (comma separated): ')
    lookup = [int(x)-1 for x in input_stats.replace(' ', '').split(',')]

    clear()
    print('Cheesecake ' + VERSION + '\n')

    cost = [{0: 0}, {0: 0}]
    result = [{0: 0}, {0: 0}]
    valid = [{0}, {0}]

    price = 'price_sell' if input_instant else 'price_buy'
    for r in c.execute('select c.id, c.description, c.duration, c.apply_count, c.type, p.'+ price +' from consumables c, prices p where c.id = p.id and c.level <= ?', (input_level,)):
        id = r[0]
        score = 0
        food = r[4] == 'Food'
        for i in lookup:
            if food:
                look = STAT_LOOKUP[i]
                p = re.search(r'((?<=\+)|^|\t|\\n)[0123456789]+(?='+look.lower()+')', r[1].lower())
            else:
                look = STAT_NAMES[i]
                p = re.search(r'(?<=gain ' + look.lower() + r' equal to )[0123456789]+(?=% of your)', r[1].lower())
            if p:
                score += int(p.group())
        score = score * (r[2]/1000) * r[3]
        x = 0 if food else 1
        cost[x][id] = r[5]
        result[x][id] = score

    for x, data in enumerate(result):
        for id, uresult in data.items():
            if uresult > 0:
                valid[x].add(id)
    
    ids, _ = f(cost, result, valid, 1, input_budget)
    total_cost = 0

    print('Optimal Food\n')
    if (ids[0] == 0):
        print('No food.')
    else:
        r = c.execute('select c.id, name, description, icon, p.' + price + ', duration, level from items i, consumables c, prices p where i.id = c.id and p.id = c.id and c.id = ?', (ids[0],)).fetchone()
        print(f'ID    : {r[0]}')
        print(f'Name  : {r[1]}')
        print(f'Level : {r[6]}')
        print(f'Time  : {r[5]/1000/60} minutes')
        print(f'Icon  : {r[3]}')
        print('Desc. :')
        print(r[2].replace('\\n', '\n'))
        print(f'Price : {moneytalk(r[4])} each')
        total_cost += r[4]
    
    print('\nOptimal Utility\n')
    if (ids[1] == 0):
        print('No utility.')
    else:
        r = c.execute('select c.id, name, description, icon, p.' + price + ', duration, level from items i, consumables c, prices p where i.id = c.id and p.id = c.id and c.id = ?', (ids[1],)).fetchone()
        print(f'ID    : {r[0]}')
        print(f'Name  : {r[1]}')
        print(f'Level : {r[6]}')
        print(f'Time  : {r[5]/1000/60} minutes')
        print(f'Icon  : {r[3]}')
        print('Desc. :')
        print(r[2].replace('\\n', '\n'))
        print(f'Price : {moneytalk(r[4])} each')
        total_cost += r[4]

    print('\nTotal Cost: ' + moneytalk(total_cost) + '\n')

    con.close()