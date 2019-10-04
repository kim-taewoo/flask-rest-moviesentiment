import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, review text, sentiment int, probability real)"
cursor.execute(create_table)

connection.commit()

connection.close()
