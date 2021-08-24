import os, shutil
import pandas as pd
from datetime import datetime
from src.orm.db_wrapper import DatabaseWrapper


class FactCheckManagerDAO(object):
    
    def __init__(self):
        self.excel_filepath_received = os.path.join('src', 'data', 'acf', 'received', 'confia.xlsx')
        self._excel_filepath_processed = os.path.join('src', 'data', 'acf', 'received', 'processed')
        
    
    def has_excel_file(self):
        return os.path.exists(self.excel_filepath_received)
    
    
    def get_checked_fakenews_from_excel(self):
        # load excel file content with pandas
        df = pd.read_excel(self.excel_filepath_received, 
                           dtype={'Id': int, 'Texto': str, 'Checagem': str, 'Link': str},
                           na_filter = False)
        
        # remove accidental blank spaces
        df['Checagem'] = df['Checagem'].apply(str.strip)
        df['Link'] = df['Link'].apply(str.strip)
        
        # filter only checked records
        df = df[df['Checagem'].notnull()]
        
        # assure value "fake"
        df['Checagem'] = df['Checagem'].str.lower()
        
        # filter only fake records, drop column 'Checagem'
        df = df[df['Checagem'] == 'fake']
        df.drop(columns=['Checagem'], inplace=True)
        
        # return dict
        df.set_index('Id', inplace=True)
        return df.to_dict(orient='index')
    
    
    def update_checked_news_in_db(self, checked_fakenews):

        # TODO: if some id record doesn't exist in the database table, register occurrence in the log
        
        try:
            dt = datetime.now()
            fakenews_ids = tuple(checked_fakenews.keys())
            
            # TODO: adds id_trusted_agency in WHERE clause
            sql_string_1 = "UPDATE detectenv.checking_outcome \
                            SET datetime_outcome = %s, \
                            is_fake = %s, \
                            trusted_agency_link = %s \
                            WHERE id_news = %s;"

            # TODO: in the future, add rule to decide between outcomes from many agencies
            sql_string_2 = "UPDATE detectenv.news \
                            SET ground_truth_label = true \
                            WHERE id_news IN %s;"
                            
            with DatabaseWrapper() as db:
                for id_news, v in checked_fakenews.items():
                    _, link = v.values()
                    args = (dt, True, link, id_news)
                    db.execute(sql_string_1, args)
                    
                db.execute(sql_string_2, (fakenews_ids,))
        except:
            raise
        
        
    def store_excel_file(self):
        shutil.move(self.excel_filepath_received, os.path.join(self._excel_filepath_processed, '{}.xlsx'.format(datetime.now())))
        
        
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
