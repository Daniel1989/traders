import sqlite3

table_name = 'traders.db'


def query_users():
    conn = sqlite3.connect(table_name)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()[0]
    return data


def update_user(user_id, name, money, status):
    conn = sqlite3.connect(table_name)
    cursor = conn.cursor()
    sql_str = 'UPDATE users SET name = "' + name + '", money = ' + str(money) + ', status = "' + status + '" WHERE id = ' + str(user_id)
    print(sql_str)
    cursor.execute(sql_str)
    conn.commit()
    conn.close()


def add_record(user_id, goods, volume, price, type, reasons, origin_response):
    conn = sqlite3.connect(table_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (user_id, goods, volume, price, type, reasons, origin_response) VALUES (?, ?, "
                   "?, ?, ?, ?, ?)",
                   (user_id, goods, volume, price, type, "\n".join(reasons), origin_response))
    conn.commit()
    conn.close()



def init_db():
    conn = sqlite3.connect(table_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY, name TEXT UNIQUE, money INTEGER, status TEXT)''')
    cursor.execute("INSERT INTO users (name,money, status) VALUES (?, ?, ?)", ('Alice', 100000, 'active'))

    cursor.execute('''CREATE TABLE IF NOT EXISTS records
                        (id INTEGER PRIMARY KEY, user_id INTEGER, goods TEXT, volume INTEGER, price INTEGER, type TEXT, reasons TEXT, origin_response TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_status
                        (id INTEGER PRIMARY KEY, user_id INTEGER, goods TEXT, volume INTEGER, price INTEGER, type TEXT, stop_loss INTEGER, take_profit INTEGER, )''')
    conn.commit()
    conn.close()


def alert_table():
    conn = sqlite3.connect(table_name)
    cursor = conn.cursor()
    cursor.execute('''ALTER TABLE user_status RENAME COLUMN amount TO volume''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # init_db()
    # print(query_users())
    alert_table()
