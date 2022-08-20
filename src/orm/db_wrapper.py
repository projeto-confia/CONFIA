import psycopg2
import numpy as np
from tenacity import *
from src.config import Config as config
from psycopg2.extras import execute_values
from psycopg2.extensions import register_adapter, AsIs

class DatabaseWrapper:

    @retry(reraise=True, stop=stop_after_attempt(15), wait=wait_random(min=5, max=10))
    def __init__(self):
        self._conn = psycopg2.connect(user=config.DATABASE.USER,
                                        password=config.DATABASE.PASSWORD,
                                        host=config.DATABASE.HOST,
                                        port=config.DATABASE.PORT,
                                        database=config.DATABASE.NAME)

        self._csr = self._conn.cursor()
        self._register_adapters()


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._csr

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def row_count(self):
        return self.cursor.rowcount
    
    def execute_many_values(self, sql, arglist=None):
        if not len(arglist):
            arglist = ()
        return execute_values(self.cursor, sql, arglist)

    def _addapt_numpy_float64(x, numpy_float64):
        return AsIs(numpy_float64)

    def _addapt_numpy_int64(x, numpy_int64):
        return AsIs(numpy_int64)

    def _addapt_numpy_float32(x, numpy_float32):
        return AsIs(numpy_float32)

    def _addapt_numpy_int32(x, numpy_int32):
        return AsIs(numpy_int32)

    def _addapt_numpy_array(x, numpy_array):
        return AsIs(tuple(numpy_array))
    
    def _addapt_numpy_bool_(x, numpy_bool_):
        return AsIs(numpy_bool_)
    
    # def _addapt_numpy_datetime64(x, numpy_datetime64):
    #     return pd.Timestamp(numpy_datetime64).to_pydatetime()

    def _register_adapters(self):
        register_adapter(np.float64, self._addapt_numpy_float64)
        register_adapter(np.int64, self._addapt_numpy_int64)
        register_adapter(np.float32, self._addapt_numpy_float32)
        register_adapter(np.int32, self._addapt_numpy_int32)
        register_adapter(np.ndarray, self._addapt_numpy_array)
        register_adapter(np.bool_, self._addapt_numpy_bool_)
        # register_adapter(np.datetime64, self._addapt_numpy_datetime64)
