import sqlite3
from sg_requests import SgRequests

def nb_entry():
    conn = sqlite3.connect(SgRequests.sqlite_db_name)
    c = conn.cursor()
    q = 'SELECT count(*) FROM ENTRY'
    c.execute(q)
    nb_entry = c.fetchone()[0]
    conn.close()
    return nb_entry

def average_point():
    conn = sqlite3.connect(SgRequests.sqlite_db_name)
    c = conn.cursor()
    q = 'SELECT avg(POINT) FROM ENTRY'
    c.execute(q)
    avg = c.fetchone()[0]
    conn.close()
    return avg

def stat_per_game():
    conn = sqlite3.connect(SgRequests.sqlite_db_name)
    c = conn.cursor()
    q = 'SELECT NAME, count(NAME), sum(POINT) FROM ENTRY GROUP BY NAME ORDER BY count(POINT) DESC'
    c.execute(q)
    avg = c.fetchall()
    conn.close()
    return avg


def print_stat():
    stat = stat_per_game()
    for a,b,c in stat:
        print(a, ' ', b, ' ', c)
    print()
    print('Total entry : ', nb_entry())
    print('Average point per entry : ', average_point())

if __name__ == '__main__':
    print_stat()
