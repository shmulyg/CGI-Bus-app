import sqlite3

conn = sqlite3.connect("bus_log.db")
c = conn.cursor()

# Create students table
c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    bus TEXT,
    bunk TEXT,
    barcode TEXT,
    status TEXT
)
''')

# Create logs table
c.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT,
    bus_number TEXT,
    timestamp TEXT
)
''')

conn.commit()
conn.close()
print("✅ Database and tables created in bus_log.db")
