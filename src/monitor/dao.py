from src.orm.db_wrapper import DatabaseWrapper
import datetime
import sys
import csv, os

class MonitorDAO(object):
    """
    docstring
    """

    def __init__(self):
        self._tweet_csv_header = ['name_social_media', 'id_account_social_media', 'screen_name',
                                  'date_creation', 'blue_badge', 'id_post_social_media', 
                                  'parent_id_post_social_media', 'text_post', 'num_likes', 'num_shares', 'datetime_post']
        
        self._tweet_csv_filename = 'tweets.csv'
        self._tweet_csv_path = os.path.join("src", "data", self._tweet_csv_filename)
        self._id_social_media = None


    def insert_posts(self):
        """
        docstring
        """

        # carrega o arquivo csv
        data = self._load_csv_to_dict(self._tweet_csv_path, fieldnames=self._tweet_csv_header, delimiter=';')

        # inicia a transação
        try:
            with DatabaseWrapper() as db:
                for post in data:

                    # separa os dados por tabela
                    social_media_data = {k:post[k] for k in list(self._tweet_csv_header[:1])}
                    account_data = {k:post[k] for k in list(self._tweet_csv_header[1:5])}
                    post_data = {k:post[k] for k in list(self._tweet_csv_header[5:])}
                    news_data = {'text_news': post['text_post'],
                                 'datetime_publication': post['datetime_post']}

                    # consulta se a pessoa já possui registro de conta na rede social
                    id_social_media_account = self._get_id_social_media_account(account_data, db)
                    if not id_social_media_account:
                        # insere ou recupera o id da pessoa que publicou o post
                        # TODO: verificar se vamos implementar

                        # insere ou recupera o id da rede social
                        # TODO: implementar e substituir o bloco abaixo

                        # recupera o id da rede social
                        if self._id_social_media is None:
                            self._id_social_media = self._get_id_social_media(social_media_data, db)
                        
                        # insere a conta e recupera o id
                        account_data['id_social_media'] = self._id_social_media
                        account_data["probalphan"] = 0.5
                        account_data["probbetan"] = 0.5
                        account_data["probumalphan"] = 0.5
                        account_data["probumbetan"] = 0.5
                        id_social_media_account = self._insert_record('detectenv.social_media_account',
                                                                      account_data,
                                                                      'id_social_media_account',
                                                                      db)

                    # consulta se a notícia já possui registro no banco
                    id_news = self._get_id_news(news_data, db)
                    if not id_news:
                        # insere a notícia e recupera o id
                        id_news = self._insert_record('detectenv.news',
                                                      news_data,
                                                      'id_news',
                                                      db)

                    # insere o post
                    post_data['id_social_media_account'] = id_social_media_account
                    post_data['id_news'] = id_news
                    if not post_data['parent_id_post_social_media']:
                        post_data['parent_id_post_social_media'] = None
                    self._insert_record('detectenv.post',
                                        post_data,
                                        'id_post',
                                        db)

            # deleta o arquivo csv ou registra no log (e-mail) caso negativo
            os.remove(self._tweet_csv_path)

        except Exception as e:
            self._error_handler(e)
            raise


    def write_in_csv_from_dict(self, data, file_path):
        with open(file_path, mode='a') as f:
            writer = csv.DictWriter(f, data.keys(), delimiter=';')
            writer.writerow(data)


    def _load_csv_to_dict(self, file_path, fieldnames, delimiter=','):
        """
        Carrega um arquivo csv

        Retorno
        --------
        data: list of dicts
        """

        data = list()
        with open(file_path) as f:
            reader = csv.DictReader(f, fieldnames=fieldnames, delimiter=delimiter)
            for row in reader:
                data.append(row)
        return data


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


    # TODO: refatorar para função genéria _get_id_record
    def _get_id_social_media_account(self, ac_data, db):
        """
        Recupera o id da conta na rede social

        Parâmetros
        -----------
        ac_data: dict
            Dicionário contendo os dados da conta na rede social

        db: DatabaseWrapper
            Instância de conexão com o banco de dados

        Retorno
        ----------
        id: int
            id se já está registrado, 0 caso contrário
        """

        sql_string = "SELECT id_social_media_account from detectenv.social_media_account where id_account_social_media = %s;"
        arg = ac_data['id_account_social_media']
        record = db.query(sql_string, (arg,))
        return 0 if not len(record) else record[0][0]


    def _get_id_social_media(self, sm_data, db):
        """
        Recupera o id da rede social

        Parâmetros
        -----------
        sm_data: dict
            Dicionário contendo os dados da rede social

        db: DatabaseWrapper
            Instância de conexão com o banco de dados

        Retorno
        ----------
        id: int
            id se já está registrado, 0 caso contrário
        """

        sql_string = "SELECT id_social_media from detectenv.social_media where upper(name_social_media) = upper(%s);"
        arg = sm_data['name_social_media']
        record = db.query(sql_string, (arg,))
        # print('id_social_media', record)
        return 0 if not len(record) else record[0][0]


    def _get_id_news(self, news_data, db):
        """
        Recupera o id da notícia

        Parâmetros
        -----------
        news_data: dict
            Dicionário contendo os dados da notícia

        db: DatabaseWrapper
            Instância de conexão com o banco de dados

        Retorno
        ----------
        id: int
            id se já está registrado, 0 caso contrário
        """

        sql_string = "SELECT id_news from detectenv.news where upper(text_news) = upper(%s);"
        arg = news_data['text_news']
        record = db.query(sql_string, (arg,))
        # print('id_news', record)
        return 0 if not len(record) else record[0][0]


    def _error_handler(self, err):
        """
        docstring
        """
        _, _, traceback = sys.exc_info()
        print ("\n{}: {} on line number {}".format(type(err).__name__, err, traceback.tb_lineno))
        print(traceback.tb_frame, '\n')


