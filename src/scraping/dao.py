from src.orm.db_wrapper import DatabaseWrapper
import csv, os


class ScrapingDAO(object):
    """
    docstring
    """

    def __init__(self):
        self._article_csv_header = ['name_agency',
                                    'publication_external_id', 
                                    'publication_title', 
                                    'publication_url', 
                                    'publication_datetime', 
                                    'publication_tags']
        self._article_csv_filename = 'articles.csv'
        self._article_csv_path = os.path.join("src", "data", self._article_csv_filename)
        self._id_agency = None


    def insert_articles(self, initial_load):
        """
        docstring
        """

        # carrega o arquivo csv
        try:
            # TODO: fazer uma chamada da biblioteca 'os' do python, para verificar se o arquivo existe
            #       se o arquivo não existir, tratar o retorno de acordo com initial_load
            data = self._load_csv_to_dict(self._article_csv_path, fieldnames=self._article_csv_header, delimiter=';')
        except:
            # TODO: transferir o teste condicional para o arquivo scraping.py
            if initial_load:
                raise
            else:
                # print('\tData file not found!')
                # print('\tNo new articles persisted.')
                return

        # inicia a transação
        try:
            with DatabaseWrapper() as db:
                for article in data:
                    
                    # separa os dados
                    agency_data = {k:article[k] for k in list(self._article_csv_header[:1])}
                    publication_data = {k:article[k] for k in list(self._article_csv_header[1:])}
                    
                    # recupera o id da agencia de checagem de fatos
                    if self._id_agency is None:
                        id = self._get_id_agency(agency_data, db)
                        self._id_agency = id if id else self._insert_record('detectenv.trusted_agency',
                                                                             agency_data,
                                                                             'id_trusted_agency',
                                                                             db)
                    
                    # insere o artigo
                    publication_data['id_trusted_agency'] = self._id_agency
                    self._insert_record('detectenv.agency_news_checked',
                                        publication_data,
                                        'id_news_checked',
                                        db)

            # deleta o arquivo csv ou registra no log (e-mail) caso negativo
            os.remove(self._article_csv_path)

        except:
            raise


    def write_in_csv_from_dict(self, data, file_path):
        with open(file_path, mode='a') as f:
            writer = csv.DictWriter(f, data.keys(), delimiter=';')
            writer.writerow(data)


    def get_last_article_datetime(self):
        """
        Recupera o maior datetime de publicação de artigo

        Retorno
        ----------
        datetime: datetime
            datetime se existe registro, 0 caso contrário
        """
        sql_string = "SELECT MAX(ag.publication_datetime) FROM detectenv.agency_news_checked ag;"
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string)
            return 0 if not len(record) else record[0][0]
        except:
            raise
        
        
    def get_num_storaged_articles(self, name_agency):
        sql_string = "SELECT COUNT(an.id_news_checked) \
                        FROM detectenv.trusted_agency a inner join detectenv.agency_news_checked an \
                            on an.id_trusted_agency = a.id_trusted_agency \
                        WHERE upper(a.name_agency) = upper(%s);"
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, (name_agency,))
            return record[0][0]
        except:
            raise
            
        
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
    def _get_id_agency(self, agency_data, db):
        """
        Recupera o id da agência de checagem de fatos

        Parâmetros
        -----------
        agency_data: dict
            Dicionário contendo os dados da agência de checagem

        db: DatabaseWrapper
            Instância de conexão com o banco de dados

        Retorno
        ----------
        id: int
            id se já está registrado, 0 caso contrário
        """

        sql_string = "SELECT id_trusted_agency from detectenv.trusted_agency where upper(name_agency) = upper(%s);"
        arg = agency_data['name_agency']
        record = db.query(sql_string, (arg,))
        # print('id_news', record)
        return 0 if not len(record) else record[0][0]
