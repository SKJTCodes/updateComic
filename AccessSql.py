import mysql.connector as mysql


class SQL:
    def __init__(self, user, pwd, host, db):
        c = mysql.connect(user=user, password=pwd, host=host, port=3306, database=db)
        self. conn = c

    def query(self, q_str):
        cur = self.conn.cursor()
        cur.execute(q_str)
        return cur.fetchall()

    def set_update(self):
        self.conn.commit()

