import xlsxwriter
import numpy as np
import pandas as pd
import datetime as dt
from pathlib import Path
from src.config import Config as config

def build_excel_sheet(candidates_to_check: list[tuple[int, str]]) -> None:
        """Build an excel file containing the candidate news to be checked by the FCAs.

        Args:
            candidates_to_check (list[tuple[int, str]): list of candidate news to be checked.
        """
        file_name = Path(f"{config.INTERVENTOR.PATH_NEWS_TO_SEND_AS_EXCEL_SHEET_TO_FCAs}", f"{dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d')}_noticias_candidatas_para_ACF.xlsx")
        
        df_news = pd.DataFrame(candidates_to_check, columns=["identificador", "noticia_a_ser_checada"])
        df_news["É Fake? (Sim/Não)"] = np.NaN
        df_news["Link ou referência da ACF"] = np.NaN
        
        df_news.rename(columns={"identificador": "Identificador", "noticia_a_ser_checada": "Notícia a ser checada"}, inplace=True)
        
        sheet_name = "Noticias para Checagem"
        
        with pd.ExcelWriter(file_name, engine='xlsxwriter', mode='w') as writer:
            df_news.to_excel(writer, sheet_name=sheet_name, startrow=2, index=False)

            with writer.book as workbook:
                worksheet = writer.sheets[sheet_name]
                
                # add the title to the excel.
                worksheet.write(0,0, f"NOTÍCIAS PARA CHECAGEM - {dt.datetime.strftime(dt.datetime.now(), '%d/%m/%Y')}", \
                    workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'}))
                
                # format main header
                merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter', 'font_size': 14, 'fg_color': '#FDE9D9'})
                
                worksheet.merge_range('A1:D2', f"NOTÍCIAS PARA CHECAGEM - {dt.datetime.strftime(dt.datetime.now(), '%d/%m/%Y')}", merge_format)
                
                # formats the header of the excel.
                header_format = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'border': 1})
                
                for col_num, value in enumerate(df_news.columns.values):
                    worksheet.write(2, col_num, value, header_format)
                    
                # add border to the table.
                border_fmt = workbook.add_format({'bottom':1, 'top':1, 'left':1, 'right':1})
                worksheet.conditional_format(xlsxwriter.utility.xl_range(0, 0, len(df_news)+2, len(df_news.columns)-1), {'type': 'no_errors', 'format': border_fmt})
                
                # center the values of the worksheet, except the second.
                format = workbook.add_format({'align': 'center'})
                
                # set column widths.
                worksheet.set_column(0, 0, 16, format)
                worksheet.set_column(1, 1, 250)
                worksheet.set_column(2, 3, 30, format)
                
        return f"Planilha de notícias para checagem gerada com sucesso em {file_name}."