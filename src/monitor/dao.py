import itertools
from operator import ne
from joblib.parallel import cpu_count
from operator import itemgetter
from src.orm.db_wrapper import DatabaseWrapper
from src.utils.text_preprocessing import TextPreprocessing
from concurrent import futures
import multiprocessing as mp
import csv, os, math
import pickle as pkl
import numpy as np

class MonitorDAO(object):
    """Funcionalidades DAO voltadas para o módulo de monitoramento. 

    Args:
        batch_size (int): o tamanho do batch que será lida do arquivo de texto de notícias recuperado do banco de dados para comparação (deduplicação). 
    """

    def __init__(self):

        self._tweet_csv_header = ['name_social_media', 'id_account_social_media', 'screen_name',
                                  'date_creation', 'blue_badge', 'id_post_social_media', 
                                  'parent_id_post_social_media', 'text_post', 'num_likes', 'num_shares', 'datetime_post']
        
        self._tweet_csv_filename = 'tweets.csv'
        self._tweet_csv_path = os.path.join("src", "data", self._tweet_csv_filename)
        self._tweet_pkl_filename = 'tweets.pkl'
        self._tweet_pkl_path = os.path.join("src", "data", self._tweet_pkl_filename)
        self._id_social_media = None
        self._text_processor = TextPreprocessing()

    def insert_posts(self):
        """
        docstring
        """
        
        # TODO: incluir testes de existência do arquivo e existẽncia de registros (file_exists, has_data)

        # carrega o arquivo csv
        data = self._load_csv_to_dict(self._tweet_csv_path, fieldnames=self._tweet_csv_header, delimiter=';')

        # inicia a transação
        try:
            with DatabaseWrapper() as db:
                total_news_db = db.query("select count(*) from detectenv.news;")[0][0]
                
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
                    news_with_biggest_score = read_cleaned_news_db_in_parallel(news_data, total_news_db)
                    print(news_data["text_news"], news_with_biggest_score)
                    
                    if not news_with_biggest_score[2]:
                        # insere a notícia e recupera o id
                        id_news = self._insert_record('detectenv.news',
                                                      news_data,
                                                      'id_news',
                                                      db)

                    # insere o post
                    post_data['id_social_media_account'] = id_social_media_account
                    post_data['id_news'] = int(id_news)
                    
                    if not post_data['parent_id_post_social_media']:
                        post_data['parent_id_post_social_media'] = None
                    
                    self._insert_record('detectenv.post',
                                        post_data,
                                        'id_post',
                                        db)

            # deleta o arquivo csv ou registra no log (e-mail) caso negativo
            os.remove(self._tweet_csv_path)

        except:
            raise

    def write_in_csv_from_dict(self, data, file_path):
        with open(file_path, mode='a') as f:
            writer = csv.DictWriter(f, data.keys(), delimiter=';')
            writer.writerow(data)
            
            
    def write_in_pkl(self, data_list):
        """Persist a list of objects within a pickle file

        Args:
            data_list (list): list of objects (list, dict, tuple, etc) that will be persisted
        """
        with open(self._tweet_pkl_path, 'ab') as f:
            for data in data_list:
                pkl.dump(data, f)
            
            
    def get_media_accounts(self, name_social_media):
        sql_string = 'select sma.id_social_media_account, sma.screen_name, sma.id_account_social_media, \
                        CASE WHEN count(p.*) > 0 THEN false ELSE true END as initial_load \
                      from detectenv.owner o inner join detectenv.social_media_account sma on \
                                                  sma.id_owner = o.id_owner \
                                             left join detectenv.post p on \
							                      p.id_social_media_account = sma.id_social_media_account \
                      where o.is_media \
                          and o.is_media_activated \
                          and sma.id_social_media = \
                              (select sm.id_social_media \
                               from detectenv.social_media sm \
                               where upper(sm.name_social_media) = upper(%s)) \
                      group by sma.id_social_media_account, sma.screen_name, sma.id_account_social_media;'

        with DatabaseWrapper() as db:
            return db.query(sql_string, (name_social_media,))
    
    
    def insert_posts_from_pkl(self):
        
        """Carrega o arquivo pickle e persiste os dados no banco
        """
        
        if not os.path.exists(self._tweet_pkl_path):
            return
        
        data = self._load_pkl(self._tweet_pkl_path)
        
        # inicia a transação
        try:
            with DatabaseWrapper() as db:
                total_news_db = db.query("select count(*) from detectenv.news;")[0][0]

                for tweet in data:
                    news_data = {'text_news': tweet['text_post'],
                                 'datetime_publication': tweet['datetime_post'],
                                 'ground_truth_label': False}                  

                    # consulta se a notícia já possui registro no banco
                    news_with_biggest_score = read_cleaned_news_db_in_parallel(news_data, total_news_db)
                    
                    if not news_with_biggest_score[2]:
                        # insere a notícia e recupera o id
                        id_news = self._insert_record('detectenv.news',
                                                      news_data,
                                                      'id_news',
                                                      db)
                    else:
                        print(f"Notícia {news_data['text_news']} similar à noticia {id_news} no BD com valor de {news_with_biggest_score[1]}.")

                    # insere o tweet
                    tweet['parent_id_post_social_media'] = tweet['parent_id_post_social_media'] or None  # empty str to None
                    tweet['id_news'] = id_news
                    self._insert_record('detectenv.post',
                                        tweet,
                                        'id_post',
                                        db)

            # deleta o arquivo pickle
            os.remove(self._tweet_pkl_path)
        except:
            raise        
        
    def get_last_media_post(self, id_social_media_account):
        """Recupera o maior datetime de publicação de post

        Args:
            id_social_media_account (int): Id da conta da media na rede social

        Returns:
            datetime: Maior datetime de publicação armazenado no banco
        """
        sql_string = "SELECT MAX(p.datetime_post) \
                      FROM detectenv.post p \
                      WHERE p.id_social_media_account = %s;"
        try:
            with DatabaseWrapper() as db:
                record = db.query(sql_string, params=(id_social_media_account,))
                return record[0][0]
        except:
            raise


    def _load_pkl(self, filepath):
        """Recupera os dados de um arquivo pickle.

        Args:
            filepath (str): File path do arquivo pickle

        Returns:
            list: Lista de objetos do arquivo pickle
        """
        data = []
        with open(filepath, 'rb') as f:
            try:
                while True:
                    data.append(pkl.load(f))
            except EOFError:
                pass
        return data
        
        
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

        return 0 if not len(record) else record[0][0]
    
    def clean_and_save_text_news(self):
        
        with DatabaseWrapper() as db:
            no_cleaned_news = self._get_no_cleaned_text_news(db)

            if no_cleaned_news != False:
                for news in no_cleaned_news:
                    news_aux = [news[0], news[1]]
                    news_aux[1] = self._text_processor.text_cleaning(news[1])
                    self._update_no_cleaned_news_with_cleaned_text(news_aux, db)
                return True

            return False

    def _get_no_cleaned_text_news(self, db):
        sql_string = "select id_news, text_news from detectenv.news where text_news_cleaned is null;"
        no_cleaned_news = db.query(sql_string)
        return False if not len(no_cleaned_news) else no_cleaned_news

    def _update_no_cleaned_news_with_cleaned_text(self, news, db):
        sql_string = "update detectenv.news set text_news_cleaned = %s where id_news = %s;"
        db.execute(sql_string, (news[1], news[0],))
        db.commit()

def read_cleaned_news_db_in_parallel(news_data, total_news_db):
    """Lê o arquivo de notícias processadas recuperadas do BD em paralelo e retorna o índice da notícia deduplicada.

    Args:
        news_data (dict): dicionário contendo os dados da notícia oriunda do streaming.
        total_news_db (int): quantidade atual de notícias no BD.

    Returns:
        indice (int): o índice da notícia duplicada no arquivo de texto.
    """
    pool = mp.Pool(mp.cpu_count())
    results = []

    for batch in _get_indices_batches_news_db(total_news_db, batch_size=128):
        results.append(pool.apply_async(_is_news_in_db, (news_data, batch,)))

    pool.close()
    pool.join()
    
    return sorted([result.get() for result in results], key=itemgetter(1))[-1]

def _get_indices_batches_news_db(total_news_db, batch_size = 128):
    """Calcula os índices dos batches que representam as notícias da tabela 'detectenv.news'.

    Args:
        total_news_db (int): o número total de notícias presentes no banco de dados.
        batch_size (int): o tamanho do batch de notícias.

    Yields:
        list: uma lista contendo os índices pertencentes ao intervalo (batch).
    """
    intervals = np.linspace(0, total_news_db-1, num=math.ceil(total_news_db/batch_size), dtype=int)

    for i in range(len(intervals)-1):
        yield [intervals[i], intervals[i+1]-1] if i < len(intervals)-2 else [intervals[i], intervals[i+1]]

def _is_news_in_db(news_data, batch):
    """
    Verifica se a notícia em 'news_data' já está presente no banco de dados.

    Parâmetros
    -----------
    news_data: dict
        Dicionário contendo os dados da notícia.

    batch: list
        Lista com os índices das linhas das noticías tratadas e armazenadas no arquivo de texto.

    Retorno
    ----------
    results: list
        id_news e valor de Levenshtein se já está registrado, -1 caso contrário.
    """

    try: 
        text_processor = TextPreprocessing()

        with DatabaseWrapper() as db:
            sql_string = "select id_news, text_news_cleaned from detectenv.news offset %s limit %s;"
            news_data_cleaned = text_processor.text_cleaning(news_data["text_news"])

            text_news_batch = db.query(sql_string, params=(int(batch[0]), int(batch[1]),))  
            results = []

            for id_news, text_news_cleaned in text_news_batch:
                ans, value = text_processor.check_duplications(news_data_cleaned, text_news_cleaned)
                results.append([id_news, value, ans])

            results_sorted = sorted(results, key=itemgetter(1), reverse=True) # ordena o valor da semelhança por ordem decrescente.
            return results_sorted[0] 
    except Exception as e:
        return -1

    finally:
        del text_processor

    # text_processor = TextPreprocessing()
    # news_data_cleaned = text_processor.text_cleaning(news_data["text_news"])
    # results = []
    # try:
    #     with open(os.path.join('src', 'data', 'news_cleaned.txt')) as file:
    #         results = [text_processor.check_duplications(news_data_cleaned, news) for news in list(itertools.islice(file, batch[0], batch[1]))]
    #         try:
    #             return results.index(True) + batch[0]
    #         except ValueError:
    #             return -1
    #         finally:
    #             del text_processor
    # except:
    #     return -1