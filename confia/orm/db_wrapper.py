import psycopg2
import db_config as dbc


class DatabaseWrapper:

    def __init__(self):
        try:
            self._conn = psycopg2.connect(user = dbc.DATABASE_CONFIG['user'],
                                          password = dbc.DATABASE_CONFIG['password'],
                                          host = dbc.DATABASE_CONFIG['host'],
                                          port = dbc.DATABASE_CONFIG['port'],
                                          database = dbc.DATABASE_CONFIG['database'])

            self._cursor = self._conn.cursor()

        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


if __name__ == "__main__":

    # usar o DatabaseWrapper em um contexto "with ... as" garante o commit ao final da execução do contexto
    with DatabaseWrapper() as db:

        # alguns exemplos
        # db.execute('CREATE TABLE comments(pkey INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR, comment_body VARCHAR, date_posted TIMESTAMP)')
        # db.execute('INSERT INTO comments (username, comment_body, date_posted) VALUES (?, ?, current_date)', ('tom', 'this is a comment'))
        
        # testando
        users = db.query('SELECT * FROM user_account')
        print(users)