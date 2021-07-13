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
    
    
    def get_fakenews_ids_from_excel(self):
        # load excel file content with pandas
        df = pd.read_excel(self.excel_filepath_received)
        
        # filter only checked records
        df = df[df['Checagem'].notnull()]
        
        # assure value "fake" and return ids
        df['Checagem'] = df['Checagem'].str.lower()
        
        return df[df['Checagem'] == 'fake']['Id'].tolist()
