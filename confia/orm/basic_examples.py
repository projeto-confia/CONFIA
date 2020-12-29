from confia.orm.db_wrapper import DatabaseWrapper

##############################
# INSERT
args = (('augusto', '123'),
        ('gabriel', '456'),
        ('carlos', '789')
       )

sql_string = "INSERT INTO detectenv.user_account (name_user_account, password) VALUES (%s,%s) RETURNING id_user_account;"

# usar o DatabaseWrapper em um contexto "with ... as" garante o commit ao final da execução do contexto
with DatabaseWrapper() as db:
    for tup in args:
        db.execute(sql_string, tup)
        id = db.fetchone()[0]
        print(id)


##############################
# UPDATE
args = ('444',)  # em python, uma tupla deve ser uma sequência. No caso de haver apenas 1 termo, deve ser seguido da vírgula
sql_string = "UPDATE detectenv.user_account SET password = %s;"

# usar o DatabaseWrapper em um contexto "with ... as" garante o commit ao final da execução do contexto
with DatabaseWrapper() as db:
    db.execute(sql_string, args)
    affected_rows = db.row_count()
    print(affected_rows)


##############################
# SELECT
sql_string = "SELECT name_user_account from detectenv.user_account;"

# usar o DatabaseWrapper em um contexto "with ... as" garante o commit ao final da execução do contexto
with DatabaseWrapper() as db:
    records = db.query(sql_string)
    for record in records:
        print(record[0])


##############################
# DELETE
sql_string = "DELETE from detectenv.user_account;"

# usar o DatabaseWrapper em um contexto "with ... as" garante o commit ao final da execução do contexto
with DatabaseWrapper() as db:
    db.execute(sql_string)
    affected_rows = db.row_count()
    print(affected_rows)
