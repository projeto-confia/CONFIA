import logging
from src.orm.db_wrapper import DatabaseWrapper


class EngineDAO(object):
    """DAO functionalities to support engine module

    Args:
        object (object): Python base class
    """

    def __init__(self):
        self._logger = logging.getLogger('schedule')
        
        
    def get_params_to_update(self):
        if self._environ_table_exists():
            sql_string = "SELECT id, name, type, value \
                            FROM admin_panel.env_variable env \
                            WHERE env.updated"
            with DatabaseWrapper() as db:
                return db.query(sql_string)
        else:
            return None
    
    
    def update_params_status_in_db(self, params_ids):
        sql_string = "UPDATE admin_panel.env_variable \
                SET updated = false \
                WHERE id in %s;"
        try:
            with DatabaseWrapper() as db:
                db.execute(sql_string, (params_ids, ))
        except:
            raise


    def _environ_table_exists(self):
        sql_string = "SELECT EXISTS ( \
                        SELECT FROM information_schema.tables \
                        WHERE  table_schema = 'admin_panel' \
                        AND    table_name   = 'env_variable' \
                        );"
        with DatabaseWrapper() as db:
            return db.query(sql_string)[0][0]
