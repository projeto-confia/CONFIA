import threading
import logging
from src.monitor.facade import MonitorFacade
from src.detection.facade import DetectorFacade
from src.scraping.facade import ScrapingFacade
from src.fcmanager.facade import FactCheckManagerFacade
from src.interventor.facade import InterventorFacade
from src.config import Config as config
from src.engine.dao import EngineDAO
from src.utils.process import get_processes
import os, subprocess
from datetime import datetime
from src.utils.email import EmailAPI


class EngineManager(object):
    
    def __init__(self) -> None:
        self._dao = EngineDAO()
        # self._logger = logging.getLogger()

    
    def run(self):
        print('Running Engine Manager...')
        if not self._is_automata_process_running():
            print('Automata is not running. Starting recovery...')
            self._delete_not_processed_data()
            self._backup_system_log()
            self._start_automata()
            self._send_recovery_notification()
        # Verificar status da Engine (stopped, running, error)
            # OBS1: Essa verificação será realizada por meio de arquivo que será mantido pela Engine do ciclo principal
            # OBS2: A localização do arquivo ainda será definada.
        # Caso status == error
            # Parar o processo do automata no S.O.
            # Go to 2)
        # Caso status == stopped
            # Recuperar do banco de dados possível nova configuração a ser aplicada
        params_to_update = self._dao.get_params_to_update()
        for param in params_to_update:
            print('Param:', param)
            # Caso exista:
                # Parar o processo do automata no S.O.
                # Reescrever o arquivo config.py com a nova configuração
                # Iniciar o processo do automata no S.O.
                # Atualizar no banco de dados o status da aplicação dos novos parâmetros
    
                
    def _is_automata_process_running(self):
        processes = get_processes('python')
        for process in processes:
            cmdline = ' '.join(process['cmdline'])
            if cmdline.endswith('python -m src'):
                return True
        return False
    
    
    def _delete_not_processed_data(self):
        print('Deleting not processed data...')
        try:
            filenames = os.listdir(os.path.join('src', 'data'))
            for filename in filenames:
                if filename == '.gitkeep':
                    continue
                filepath = os.path.join('src', 'data', filename)
                os.remove(filepath)
                print(f'File {filepath} removed.')
        except:
            print('Error while trying to delete not processed data.')
            raise
            
            
    def _backup_system_log(self):
        print('Backing up system logs...')
        try:
            system_log_filepath = os.path.join('logs', 'nohup.out')
            if not os.path.exists(system_log_filepath):
                print(f'File {system_log_filepath} not found.')
                return
            with open(system_log_filepath, 'r') as file_source:
                data = file_source.read()
            with open(os.path.join('logs', 'nohup.bkp.out'), 'a+') as file_target:
                file_target.write(f'## SYSTEM RECOVERY BACKUP AT {datetime.now()}')
                file_target.write('\n')
                file_target.write(data)
                file_target.write('\n')
            os.remove(system_log_filepath)
        except:
            print('Error while trying to backup system logs.')
            raise
        
        
    def _start_automata(self):
        print('Starting automata...')
        try:
            subprocess.run(["./automata.sh"])
        except:
            print('Error while trying to start automata.')
            raise

        
    def _send_recovery_notification(self):
        print('Sending recovery notification...')
        try:
            EmailAPI().send([config.EMAIL.ACCOUNT],
                            text_subject='AUTOMATA app recovered.',
                            text_message='AUTOMATA app was not running but the recovery system brought everything back to normal.\n\nEverything is ok now =D')
        except:
            print('Error while trying to send recovery notification.')
            raise
            

class Engine(object):
    """
    docstring
    """

    def __init__(self):
        
        # logging
        self._logger = logging.getLogger(config.LOGGING.NAME)
        self.engine_status = config.STATUS.STOPPED
        self._logger.info('System ready.')


    def restart(self):
        """
        docstring
        """
        # TODO: implementar
        # load config


    def run(self):
        """
        docstring
        """
        threading.Timer(config.ENGINE.FREQUENCY, self.run).start()
        if self.engine_status == config.STATUS.RUNNING :
            self._logger.warning("Engine in processing. Impossible start a new one.")
        elif self.engine_status == config.STATUS.STOPPED:
            self.run_process()
        else:
            self._logger.error("Engine unavailable.")


    def run_process(self):
        try:
            self._logger.info('Running process...')
            self.engine_status = config.STATUS.RUNNING
            
            if config.ENGINE.SCRAPING_ACTIVATED:
                ScrapingFacade().run()
            if config.ENGINE.FACT_CHECK_MANAGER_ACTIVATED:
                FactCheckManagerFacade().run()
            if config.ENGINE.MONITOR_ACTIVATED:
                MonitorFacade().run()
            if config.ENGINE.DETECTOR_ACTIVATED:
                DetectorFacade().run()
            if config.ENGINE.INTERVENTOR_ACTIVATED:
                InterventorFacade().run()
            
            self.engine_status = config.STATUS.STOPPED
            self._logger.info('Process finished.')
        except:
            self.engine_status = config.STATUS.ERROR
            self._logger.critical('Engine in critical status.', exc_info=True)
            raise
