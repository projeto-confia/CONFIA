from confia.orm.db_wrapper import DatabaseWrapper
import datetime
import sys

class MonitorDAO(object):
    """
    docstring
    """

    def __init__(self):
        pass


    def insert_posts(self):
        """
        docstring
        """

        # carrega o arquivo csv

        # inicia a transação

        # para cada registro csv:
        
            # consulta se a pessoa já possui registro de conta na rede social
                # sim 
                    # recupera o id da conta na rede social
                # não
                    # insere ou recupera o id da pessoa que publicou o post
                    # insere ou recupera o id da rede social
                    # insere a conta na rede social e recupera o id da conta na rede social

            # consulta se a notícia já possui registro no banco
                # sim
                    # recupera o id da notícia
                # não
                    # insere a notícia e recupera o id

            # insere o post

        # comita a transação

        # deleta o arquivo csv ou registra no log (e-mail) caso negativo

        try:
            data = dict(name_social_media='linkedin',
                    screen_name='augusto', 
                    date_creation=datetime.datetime.now(), 
                    blue_badge=True,
                    id_account = '333333333333')

            social_media_data = {x:data[x] for x in ['name_social_media']}
            account_data = {x:data[x] for x in ['screen_name', 'date_creation', 'blue_badge', 'id_account']}

            # usar o DatabaseWrapper em um contexto "with ... as" garante o commit ao final da execução do contexto
            with DatabaseWrapper() as db:
                id_social_media = self._insert_record('detectenv.social_media', 
                                        social_media_data,
                                        'id_social_media',
                                        db)
                print('id_social_media', id_social_media)
                account_data['id_social_media'] = id_social_media
                id_account = self._insert_record('detectenv.social_media_account',
                                                account_data,
                                                'id_social_media_account',
                                                db)
                print('id_account', id_account)
        except Exception as e:
            self._error_handler(e)
            raise


    def _load_csv(self, file_path):
        """
        Carrega o arquivo csv resultante da coleta
        """
        pass


    def _delete_csv(self, file_path):
        """
        Deleta o arquivo csv resultante da coleta
        """
        pass


    def _insert_record(self, tablename, data, returning, db):
        """
        Insere um registro no banco de dados

        Parâmetros
        ----------
        tablename: str
            String contendo o schema e a tabela no banco de dados
            Exemplo: public.owner

        data: dict
            Dicionário contendo os campos e valores a serem inseridos
            A chave deve refletir o nome do campo na referida tabela do banco de dados

        returning: str
            String contendo o nome do campo da chave primária
            exemplo: id_owner

        Retorno
        -------
        id: int
            Chave primária do registro no banco de dados
        """

        cols = ', '.join(list(data.keys()))
        values_placeholder = ','.join(['%s']*len(data.keys()))
        sql_string = "INSERT INTO {} ({}) VALUES ({}) RETURNING {};".format(tablename, 
                                                                            cols, 
                                                                            values_placeholder, 
                                                                            returning)
        # print(sql_string)
        db.execute(sql_string, list(data.values()))
        return db.fetchone()[0]


    def _error_handler(self, err):
        """
        docstring
        """
        _, _, traceback = sys.exc_info()
        print ("\n{}: {} on line number {}".format(type(err).__name__, err, traceback.tb_lineno))
        print(traceback.tb_frame, '\n')
