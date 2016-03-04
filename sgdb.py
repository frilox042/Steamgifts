import sqlite3


class SgDb(object):
    def __init__(self, sqlite_db_name):
        self.sqlite_db_name = sqlite_db_name

    def check_if_already_entered(self, giveaway_code):
        conn = sqlite3.connect(self.sqlite_db_name)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM ENTRY WHERE CODE= (?)", (giveaway_code,))
        res = c.fetchone()[0] == 1
        conn.close()
        return res

    def add_an_entry(self, giveaway_code, giveaway_price, giveaway_link):
        conn = sqlite3.connect(self.sqlite_db_name)
        c = conn.cursor()
        name = giveaway_link.split('/')[3]
        c.execute("INSERT INTO ENTRY VALUES(?,?,?)",
                  (giveaway_code, giveaway_price, name))
        conn.commit()
        conn.close()

    def setup(self):
        conn = sqlite3.connect('sg_entry.db')
        c = conn.cursor()
        c.execute('CREATE TABLE ENTRY (CODE text, POINT int, NAME text)')
        #Never remember, if I have or not to commit for creating table
        conn.commit()
        conn.close()

def main():
    db = SgDb("sg_entry.db")
    db.setup()

if __name__ == "__main__":
    main()
