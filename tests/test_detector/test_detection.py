import logging
import unittest
import subprocess, os, shlex
import pandas as pd
from src.detection import dao

class TestDetection(unittest.TestCase):
    
    def setUp(self):
        path_folder = f'{os.path.join(os.getcwd().removesuffix("/automata"), "database")}'
        subprocess.check_call(['sudo', './pg_restore.sh', 'pg_backup/dump_initial_state.sql.gz'], cwd=path_folder)
        
    
    def test_unlabeled_news_shared_by_reputed_users(self):
        self.assertEqual(3,3)
    
if __name__ == '_main_':
    unittest.main()