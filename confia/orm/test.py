# teste inicial
import psycopg2
import db_config as dbc

try:
    connection = psycopg2.connect(user = dbc.DATABASE_CONFIG['user'],
                                  password = dbc.DATABASE_CONFIG['password'],
                                  host = dbc.DATABASE_CONFIG['host'],
                                  port = dbc.DATABASE_CONFIG['port'],
                                  database = dbc.DATABASE_CONFIG['database'])

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")