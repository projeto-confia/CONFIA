import os, glob
import pandas as pd
from datetime import datetime
from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper
from src.utils.singleton import SingletonMetaClass


class FactCheckManagerDAO(metaclass=SingletonMetaClass):
    
    def __init__(self):
        self._received_xlsx_path = config.FCMANAGER.RECEIVED_XLSX_FILES_PATH
        self._processed_xlsx_path = config.FCMANAGER.RECEIVED_PROCESSED_XLSX_FILES
    
    
    def has_excel_files(self) -> list[str]:
        """Check whether there are spreadsheets (.xlsx) files which came from the FCAs, and returns their names into a list.

        Returns:
            list[str]: a list of strings with the full path (including the .xlsx files). Returns '[]' if the directory is empty.
        """
        return glob.glob(os.path.join(self._received_xlsx_path, '*.xlsx'))
    
    
    def process_fake_news_from_xlsx(self, sheet: str) -> dict[int, dict]:
        """Loads the spreadsheet corresponding to the 'sheet' path, and processes its content.

        Args:
            sheet (str): a full path (including the name of the .xlsx file) to be processed.

        Returns:
            dict[int, dict]: the loaded and preprocessed dataframe with the content of the corresponding spreadsheet in dictionary format, where the keys are the ids and the values are the news' content itself.
        """
        
        # loads the excel file into a dataframe.
        df = pd.read_excel(sheet, header=2, 
                           dtype={'Identificador': int, 'Notícia a ser checada': str, 'É Fake? (Sim/Não)': str, 'Link ou referência da ACF': str})
        
        # rename the columns to facilitate the remaning processing.
        df.rename(columns={"Identificador": "id", "Notícia a ser checada": "news", "É Fake? (Sim/Não)": "is_fake", "Link ou referência da ACF": 'link_fca'}, inplace=True)
        
        # filter out the rows where 'is_fake' is blank.
        df = df[df['is_fake'].notnull()]
        
        # remove accidental blank spaces from 'is_fake' and 'link_fca' contents.
        df['link_fca'] = df['link_fca'].str.strip()
        df['is_fake'] = df['is_fake'].str.strip().str.lower()
        
        # filter out only fake news from column 'is_fake'.
        df = df[df['is_fake'] == 'sim']
        
        # fill other blank fields with empty string.
        df.fillna('', inplace=True)       

        df.set_index('id', inplace=True)        
        return df.to_dict(orient='index')

    
    def _check_existence_of_news_in_both_news_and_checking_outcome_tables(self, fake_news_ids: list[int]) -> set[int]:
        """Check whether both tables 'news' and 'checking_outcome' have the ids in 'fake_news_ids'.

        Args:
            fake_news_ids (list[int]): a list containing the ids of the news retrieved from the FCA's spreadsheet.

        Returns:
            set[int]: a set containing the news' ids which are present in both tables.
        """
        
        fake_news_ids_set = set(fake_news_ids)
        
        sql_str =  "SELECT DISTINCT * FROM ( \
                        SELECT DISTINCT n.id_news as news_id, co.id_news as fca_id_news \
                        FROM detectenv.news n, detectenv.checking_outcome co \
                        WHERE n.id_news in %s AND co.id_news in %s \
                    ) tbl WHERE tbl.news_id = tbl.fca_id_news;"

        with DatabaseWrapper() as db:    
            result = db.query(sql_str, (fake_news_ids, fake_news_ids,))
        
        if not result:
            return set()
        
        db_news_ids_set = {r[0] for r in result}
        return fake_news_ids_set.intersection(db_news_ids_set)
        
    
    def update_checked_news_in_db(self, checked_fake_news):
        
        try:
            dt = datetime.now()
            fake_news_ids = tuple(checked_fake_news.keys())
            news_ids_set = self._check_existence_of_news_in_both_news_and_checking_outcome_tables(fake_news_ids)
            
            if not news_ids_set:
                raise IndexError(f"No ids in the list {fake_news_ids} were not found in both tables 'news' and 'checking_outcome'. Please look for any missing values in these tables.")
            
            if news_ids_set != set(fake_news_ids):
                diff_ids = set(fake_news_ids).difference(news_ids_set)
                
                raise IndexError(f"Only ids '{','.join([str(n) for n in news_ids_set])}' in the list were found in both tables 'news' and 'checking_outcome'. Please look for the missing ids '{','.join([str(d) for d in diff_ids])}' in these tables.")
                
            
            # TODO: Information regarding the FCAs' ids are missing by default in 'checked_fake_news'. These data must be included when working with more FCAs later on.
            
            sql_string_1 = "UPDATE detectenv.checking_outcome \
                            SET datetime_outcome = %s, \
                            is_fake = %s, \
                            trusted_agency_link = %s \
                            WHERE id_news = %s and id_trusted_agency = %s;"

            # TODO: in the future, add rule to decide between outcomes from many agencies.
            
            sql_string_2 = "UPDATE detectenv.news \
                            SET ground_truth_label = true \
                            WHERE id_news IN %s;"
                            
            with DatabaseWrapper() as db:
                for id_news, v in checked_fake_news.items():
                    link = list(v.values())[-1]
                    args = (dt, True, link, id_news, 1) #! '1' here means 'Boatos.org' since it's the only FCA we're worked during the development of the prototype.
                    
                    db.execute(sql_string_1, args)
                    
                db.execute(sql_string_2, (fake_news_ids,))
        except:
            raise
        
    
    def get_clean_text_news_from_id(self, id_news: int) -> str:
        """Returns the cleaned text of a news given its id.

        Args:
            id_news (int): the id of the news.

        Returns:
            str: the news' clean content.
        """
        try:
            sql_str = "select text_news_cleaned from detectenv.news where id_news = %s;"
            
            with DatabaseWrapper() as db:
                text_cleaned = db.query(sql_str, (id_news,))
            
            return text_cleaned[0][0]
        
        except:
            raise
        
        
    def register_log_alert(self, id_news):
        try:
            dt = datetime.now()
            sql_string = "INSERT INTO detectenv.action_log \
                        (id_action, id_news, datetime_log, description_log) \
                        VALUES ((SELECT act.id_action \
                                FROM detectenv.action_type act \
                                WHERE upper(act.name_action) = upper('alert_checked')), \
                                %s, %s, 'alerta registrado no twitter');"
                                
            with DatabaseWrapper() as db:
                db.execute(sql_string, (id_news, dt))
        except:
            raise
