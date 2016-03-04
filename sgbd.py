import sqlite3

conn = sqlite3.connect('sg_entry.db')

c = conn.cursor()

c.execute('CREATE TABLE ENTRY (CODE text, POINT int, NAME text)')

#Never remember, if I have or not to commit for creating table
conn.commit()

conn.close()
