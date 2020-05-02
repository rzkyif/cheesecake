import items
import sqlite3
from constants import *

if __name__ == "__main__":
    items.refresh_items_database()
    con = sqlite3.connect(ITEMS_DATABASE_PATH)
    c = con.cursor()

    print('Database test:')
    print(c.execute('select * from consumables where apply_count <> 1').fetchall())

    con.close()