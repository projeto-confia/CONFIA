import os, sys
import xlsxwriter
from confia.orm.db_wrapper import DatabaseWrapper


class InterventorDAO(object):
    
    def __init__(self):
        self._excel_file_path = os.path.join('confia', 'data', 'confia.xlsx')
        self._workbook = None
    
    
    def select_candidate_news_to_check(self):
        """Select candidate news to be send to Fact Check Agencys

        Returns:
            list: list of candidates
        """
        
        sql_string =   "select n.id_news, n.text_news \
                        from detectenv.news n left join detectenv.checking_outcome co on co.id_news = n.id_news \
                                            inner join detectenv.post p on p.id_news = n.id_news \
                        where n.datetime_publication > current_date - interval '7' day \
                            and n.ground_truth_label is null \
                            and n.classification_outcome = True \
                            and co.id_news is null \
                            and n.prob_classification > 0.9 \
                        group by n.id_news, n.text_news, n.prob_classification \
                        order by max(p.num_shares) desc, n.prob_classification desc \
                        limit 4;"
        try:
            with DatabaseWrapper() as db:
                records = db.query(sql_string)
            return 0 if not len(records) else records
        except Exception as e:
            self._error_handler(e)
            raise
        
    
    def get_workbook(self):
        try:
            if not self._workbook:
                workbook = xlsxwriter.Workbook(self._excel_file_path)
                bold = workbook.add_format({'bold': True})
                text_wrap = workbook.add_format({'text_wrap': True})
                worksheet = workbook.add_worksheet('planilha1')
                worksheet.set_column(1, 1, 100, text_wrap)
                worksheet.write(0, 0, 'Id', bold)
                worksheet.write(0, 1, 'Texto', bold)
                self._workbook = workbook
            return self._workbook
        except Exception as e:
            self._error_handler(e)
            raise
        
        
    def close_workbook(self):
        self._workbook.close()
        self._workbook = None
        
        
    def _error_handler(self, err):
        _, _, traceback = sys.exc_info()
        print ("\n{}: {} on line number {}".format(type(err).__name__, err, traceback.tb_lineno))
        print(traceback.tb_frame, '\n')