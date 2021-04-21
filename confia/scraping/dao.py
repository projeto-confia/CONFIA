from confia.orm.db_wrapper import DatabaseWrapper
import datetime
import sys
import csv, os

class ScrapingDAO(object):
    """
    docstring
    """

    def __init__(self):
        self._article_csv_header = ['external_id', 'title', 'url', 'datetime', 'tags']
        self._article_csv_filename = 'articles.csv'
        self._article_csv_path = os.path.join("confia", "data", self._article_csv_filename)
        # self._id_social_media = None


    def insert_articles(self):
        """
        docstring
        """

        # carrega o arquivo csv
        data = self._load_csv_to_dict(self._article_csv_path, fieldnames=self._article_csv_header, delimiter=';')

        # inicia a transação
        try:
            with DatabaseWrapper() as db:
                for article in data:
                    
                    # insere o artigo
                    self._insert_record('detectenv.post',
                                        article,
                                        'id_news_checked',
                                        db)

            # deleta o arquivo csv ou registra no log (e-mail) caso negativo
            os.remove(self._article_csv_path)

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
 

    def _error_handler(self, err):
        """
        docstring
        """
        _, _, traceback = sys.exc_info()
        print ("\n{}: {} on line number {}".format(type(err).__name__, err, traceback.tb_lineno))
        print(traceback.tb_frame, '\n')


