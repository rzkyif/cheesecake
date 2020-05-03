import items
import prices
import sqlite3
from lib import *

if __name__ == "__main__":
    items.refresh_items_database()
    prices.refresh_prices_database()
    con = sqlite3.connect(DATABASE_PATH)
    c = con.cursor()

    print('Database test 1:')
    print(c.execute('select * from consumables where apply_count <> 1').fetchall())

    print('Database test 2:')
    print(c.execute('select name, price_buy, price_sell from consumables c, prices p where c.id = p.id').fetchall())

    con.close()