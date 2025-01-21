import sqlite3

# Check table schema using SQLite CLI or Python
conn = sqlite3.connect('instance/form_data.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(form_data);")
print(cursor.fetchall())
conn.close()