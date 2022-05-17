import os
import logging
# from src.config import Config as config
from src.orm.db_wrapper import DatabaseWrapper


class EngineDAO(object):
    """DAO functionalities to support engine module

    Args:
        object (object): Python base class
    """

    def __init__(self):
        self._logger = logging.getLogger('schedule')
        self._config_file = 'config.py'
        self._config_filepath = os.path.join("src", self._config_file)
        self._logger.info('Dao constructor')
        
        
    def get_params_to_update(self):
        if self._environ_table_exists():
            sql_string = "SELECT id, name, type, value \
                            FROM admin_panel.env_variable env \
                            WHERE env.updated"
            with DatabaseWrapper() as db:
                return db.query(sql_string)


    def _environ_table_exists(self):
        sql_string = "SELECT EXISTS ( \
                        SELECT FROM information_schema.tables \
                        WHERE  table_schema = 'admin_panel' \
                        AND    table_name   = 'env_variable' \
                        );"
        with DatabaseWrapper() as db:
            return db.query(sql_string)[0][0]
