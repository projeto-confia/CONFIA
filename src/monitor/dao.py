import pandas as pd
import multiprocessing as mp
import os
from operator import itemgetter
from datetime import datetime, timedelta
from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper
from src.utils.text_preprocessing import TextPreprocessing


class MonitorDAO(object):
    """DAO functionalities to support monitor module

    Args:
        object (object): Python base class
    """

    def __init__(self):

        self._tweet_file = 'tweets.pkl'
        self._tweet_filepath = os.path.join("src", "data", self._tweet_file)
        self._text_news_cleaned = self._get_text_news_cleaned()
      
            
    def write_in_pkl(self, df):
        """Persist data within a pickle file

        Args:
            df (pd.DataFrame, list): pandas.DataFrame or list of dict
        """
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        df.to_pickle(self._tweet_filepath)
            
            
    def get_media_accounts(self, name_social_network):
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
            return db.query(sql_string, (name_social_network,))
        
        
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
    
    
    def insert_media_posts(self):
        """Persist pickle file content into database
        """
        
        df = self._load_pkl()
        if not isinstance(df, pd.DataFrame):
            return
        df['ground_truth_label'] = False
        df['id_news'] = 0
        id_news_col_idx = df.columns.get_loc('id_news')
        groups = df.groupby(['group']).groups
        try:
            with DatabaseWrapper() as db:
                if self._text_news_cleaned:
                    df_news = self._extract_df_news_groups_firsts(df, has_ground_truth_label=True)
                    self._update_dataframe_with_similar_id_news(df, df_news, groups, id_news_col_idx)
                    df_news = self._extract_df_news_groups_firsts(df, has_ground_truth_label=True)
                    if not df_news.empty:
                        id_news_list = self._insert_news_in_db(df_news, db, has_ground_truth_label=True)
                        self._update_dataframe_with_id_news(df_news, id_news_list, df, groups)
                else:
                    df_news = self._extract_df_news_groups_firsts(df, has_ground_truth_label=True)
                    id_news_list = self._insert_news_in_db(df_news, db, has_ground_truth_label=True)
                    self._update_dataframe_with_id_news(df_news, id_news_list, df, groups)
                self._insert_posts_in_db(df, db)
            os.remove(self._tweet_filepath)
        except:
            raise
        
        
    def insert_stream_posts(self):
        """Persist pickle file content into database
        """
        
        df = self._load_pkl()
        if not isinstance(df, pd.DataFrame):
            return
        df['id_news'] = 0
        id_news_col_idx = df.columns.get_loc('id_news')
        groups = df.groupby(['group']).groups
        try:
            with DatabaseWrapper() as db:
                if self._text_news_cleaned:
                    df_news = self._extract_df_news_groups_firsts(df)
                    self._update_dataframe_with_similar_id_news(df, df_news, groups, id_news_col_idx)
                    df_news = self._extract_df_news_groups_firsts(df)
                    if not df_news.empty:
                        id_news_list = self._insert_news_in_db(df_news, db)
                        self._update_dataframe_with_id_news(df_news, id_news_list, df, groups)
                else:
                    df_news = self._extract_df_news_groups_firsts(df)
                    id_news_list = self._insert_news_in_db(df_news, db)
                    self._update_dataframe_with_id_news(df_news, id_news_list, df, groups)
                df = self._update_dataframe_with_social_network_accounts(df, db)
                self._insert_posts_in_db(df, db)
            os.remove(self._tweet_filepath)
        except:
            raise
            
        
    def _extract_df_news_groups_firsts(self, df:pd.DataFrame, has_ground_truth_label=False):
        ground_truth_label = ['ground_truth_label'] if has_ground_truth_label else []
        cols = ['text_post', 'datetime_post', 'text_prep'] + ground_truth_label
        df_news = df[df['id_news'] == 0].groupby('group').first()[cols]
        df_news.columns = ['text_news', 'datetime_publication', 'text_news_cleaned'] + ground_truth_label
        return df_news
    
    
    def _update_dataframe_with_similar_id_news(self, df:pd.DataFrame, df_news:pd.DataFrame, groups, id_news_col_idx):
        for group_key, group_row in df_news.iterrows():
            news_data = group_row.to_dict()
            id_news_db, _, is_similar = read_cleaned_news_db_in_parallel(news_data, self._text_news_cleaned)
            if is_similar:
                indices = groups[group_key]
                df.iloc[indices, id_news_col_idx] = id_news_db
                
                
    def _insert_news_in_db(self, df_news:pd.DataFrame, db:DatabaseWrapper, has_ground_truth_label=False):
            arglist = df_news.to_records(index=False)
            if has_ground_truth_label:
                arglist = [(a, pd.Timestamp(b).to_pydatetime(), c, d) for a, b, c, d in arglist]
            else:
                arglist = [(a, pd.Timestamp(b).to_pydatetime(), c) for a, b, c in arglist]
            id_news_list = self._insert_many_records('detectenv.news',
                                                        df_news.columns,
                                                        arglist,
                                                        'id_news',
                                                        db)
            return id_news_list

    
    def _update_dataframe_with_id_news(self, 
                                       df_news:pd.DataFrame, 
                                       id_news_list:list,
                                       df:pd.DataFrame, 
                                       groups):
        id_news_col_idx = df.columns.get_loc('id_news')
        for group_key, id_news in zip(df_news.index, id_news_list):
            indices = groups[group_key]
            df.iloc[indices, id_news_col_idx] = id_news[0]
            
         
    def _update_dataframe_with_social_network_accounts(self, df:pd.DataFrame, db:DatabaseWrapper):
        social_network_data = {'name_social_media': df['name_social_media'].unique()[0]}
        id_social_network = self._get_id_social_network(social_network_data, db)
        external_accounts = df['id_account_social_media'].unique()
        internal_accounts = self._get_social_networks_accounts(id_social_network,
                                                               external_accounts)
        if internal_accounts:
            df = self._update_dataframe_with_accounts(internal_accounts, df)
        cols = ['id_account_social_media', 'screen_name', 'date_creation', 'blue_badge']
        df_accounts_to_insert = df[df['id_social_media_account'].isnull()][cols].drop_duplicates()
        if df_accounts_to_insert.empty:
            return df
        id_social_media_accounts = self._insert_social_network_accounts(id_social_network, df_accounts_to_insert, db)
        internal_accounts = [(a, b[0]) for a, b in zip(df_accounts_to_insert['id_account_social_media'], id_social_media_accounts)]
        df = self._update_dataframe_with_accounts(internal_accounts, df)
        df['id_social_media_account'] = df['id_social_media_account_x'].combine_first(df['id_social_media_account_y'])
        return df


    def _get_social_networks_accounts(self,
                                      id_social_network, 
                                      external_social_network_accounts):
        
        sql_string = "SELECT sma.id_account_social_media, sma.id_social_media_account \
                        FROM detectenv.social_media_account sma \
                        WHERE sma.id_social_media = %s \
                        AND sma.id_account_social_media in %s;"
        try:
            with DatabaseWrapper() as db:
                records = db.query(sql_string, (id_social_network, external_social_network_accounts))
                return records
        except:
            raise
        
        
    def _update_dataframe_with_accounts(self, accounts, df:pd.DataFrame):
        df_internal_accounts = pd.DataFrame(accounts,
                                            columns=['id_account_social_media',
                                                     'id_social_media_account'])
        df_internal_accounts = df_internal_accounts.astype({'id_account_social_media': str,
                                                            'id_social_media_account': int})
        return df.merge(df_internal_accounts, on='id_account_social_media', how='left')
        
        
    def _insert_social_network_accounts(self, id_social_network, df_accounts:pd.DataFrame, db:DatabaseWrapper):
        df_accounts['id_social_media'] = id_social_network
        df_accounts["probalphan"] = 0.5
        df_accounts["probbetan"] = 0.5
        df_accounts["probumalphan"] = 0.5
        df_accounts["probumbetan"] = 0.5
        arglist = df_accounts.to_records(index=False)
        arglist = [(a,b, pd.Timestamp(c).to_pydatetime(), d,e,f,g,h,i) for a,b,c,d,e,f,g,h,i in arglist]
        return self._insert_many_records('detectenv.social_media_account',
                                         df_accounts.columns,
                                         arglist,
                                         'id_social_media_account',
                                         db)
        
        
    def _insert_posts_in_db(self, df:pd.DataFrame, db:DatabaseWrapper):
        cols = ['id_social_media_account', 'id_news', 'id_post_social_media',
                'parent_id_post_social_media', 'text_post', 'datetime_post',
                'num_likes', 'num_shares']
        df['parent_id_post_social_media'] = df['parent_id_post_social_media'].fillna(0)
        arglist = df.loc[:,cols].to_records(index=False)
        arglist = [(a,b,c,(d if d else None),e,pd.Timestamp(f).to_pydatetime(),g,h) for a,b,c,d,e,f,g,h in arglist]
        self._insert_many_records('detectenv.post',
                                    cols,
                                    arglist,
                                    'id_post',
                                    db)


    def _load_pkl(self, filepath=None) -> pd.DataFrame:
        """Load data from pickle file.

        Args:
            filepath (str): Pickle filepath. If not passed, self._tweet_pkl_path will be used. Defaults None

        Returns:
            pandas.DataFrame: Pandas dataframe of the pickle file or None if filepath doesn't exists
        """
        try:
            if not filepath:
                filepath = self._tweet_filepath
            if not os.path.exists(filepath):
                return None
            return pd.read_pickle(filepath)
        except:
            raise
        
        
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
    
    
    def _insert_many_records(self, tablename, cols, args, returning, db:DatabaseWrapper):
        """Insert many records into database

        Args:
            tablename (str): Table name
            cols (list): List of table columns
            args (list): List of tuples, each one related to one record to be persisted
            returning (str): Table column to return, often the PK columns
            db (DatabaseWrapper): Database conection instance

        Returns:
            list: List of values returned from database, according returning param
        """
    
        cols = ', '.join(cols)
        sql_string = f'INSERT INTO {tablename} ({cols}) VALUES %s RETURNING {returning};'
        returnings = []
        for i in range(0, len(args), 50):
            db.execute_many_values(sql_string, args[i:i+50])
            part = db.fetchall()
            returnings += part
        return returnings


    # TODO: refactor to generic function and moves to orm module
    def _get_id_social_network(self, social_network_data:dict, db:DatabaseWrapper):
        """Fetch social network's id from database

        Args:
            social_network_data (dict): Dict that must have 'name_social_media' key
            db (DatabaseWrapper): Database connection instance

        Returns:
            int: Social network's id
        """

        sql_string = "SELECT id_social_media from detectenv.social_media where upper(name_social_media) = upper(%s);"
        arg = social_network_data['name_social_media']
        record = db.query(sql_string, (arg,))
        return 0 if not len(record) else record[0][0]
    
    
    def _get_text_news_cleaned(self):
        try:
            with DatabaseWrapper() as db:
                datetime_ago = datetime.today() - timedelta(days = config.MONITOR.WINDOW_SIZE)
                sql_string = "SELECT n.id_news, n.text_news_cleaned \
                                FROM detectenv.news n \
                                WHERE n.datetime_publication >= %s;"
                records = db.query(sql_string, (datetime_ago.date(),))
                return records
        except:
            raise


def read_cleaned_news_db_in_parallel(news_data, cleaned_news_db):
    """Finds the most similar news on database

    Args:
        news_data (dict): dict that must contain 'text_news_cleaned' indice
        cleaned_news_db (list): List of cleaned news from database.

    Returns:
        news_most_similar (list): most similar news as list, with [id_news_db:int, \
            ratio_similarity:float, \
            is_similar:bool]
    """
    
    pool = mp.Pool(mp.cpu_count())
    results = []
    for batch in _get_indices_batches_news_db(len(cleaned_news_db), batch_size=128):
        results.append(pool.apply_async(_is_news_in_db, (news_data, cleaned_news_db, batch,)))
    pool.close()
    pool.join()
    return sorted([result.get() for result in results], key=itemgetter(1))[-1]


def _get_indices_batches_news_db(total_news_db, batch_size=128):
    """Calcula os índices dos batches que representam as notícias da tabela 'detectenv.news'.

    Args:
        total_news_db (int): o número total de notícias presentes no banco de dados.
        batch_size (int): o tamanho do batch de notícias.

    Yields:
        list: uma lista contendo os índices pertencentes ao intervalo (batch).
    """
    for i in range(0, total_news_db, batch_size):
        yield([i, i+batch_size])


def _is_news_in_db(news_data, cleaned_news_db, batch):
    """
    Verifica se a notícia em 'news_data' já está presente no banco de dados.

    Parâmetros
    -----------
    news_data: dict
        Dicionário contendo os dados da notícia.

    cleaned_news_db: list
        Lista contendo as notícias tratadas oriundas do banco de dados.

    batch: list
        Lista com os índices das linhas das noticías tratadas e armazenadas no arquivo de texto.

    Retorno
    ----------
    results: list
        id_news e valor de Levenshtein se já está registrado, -1 caso contrário.
    """
    
    try:
        text_processor = TextPreprocessing()
        text_news_batch = cleaned_news_db[batch[0]:batch[1]]
        results = []

        for id_news, text_news_cleaned in text_news_batch:
            ans, value = text_processor.check_duplications(news_data['text_news_cleaned'], text_news_cleaned)
            results.append([id_news, value, ans])

        results_sorted = sorted(results, key=itemgetter(1), reverse=True) # ordena o valor da semelhança por ordem decrescente.
        return results_sorted[0] 

    except Exception as e:
        # TODO: evolve this exception treatment
        return -1

    finally:
        del text_processor
