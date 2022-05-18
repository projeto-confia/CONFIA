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
from src.engine.configbuilder import ConfigBuilder


class EngineManager(object):
    
    def __init__(self) -> None:
        self._dao = EngineDAO()
        # self._logger = logging.getLogger()

    
    def run(self):
        print('Running Engine Manager...')
        if not self._is_automata_process_running():
            print('Automata is not running. Starting recovery...')
            self._recover_automata()
        automata_status = self._get_automata_status()
        if automata_status == config.STATUS.ERROR:
            print('Automata in error state. Starting recovery...')
            self._stop_automata_process()
            self._recover_automata()
        if automata_status == config.STATUS.STOPPED:
            params_to_update = self._dao.get_params_to_update()
            if params_to_update:
                self._stop_automata_process()
                print('Building new config file...')
                ConfigBuilder().build(params_to_update)
                self._start_automata()
                self._log_params_update()
                self._update_params_status_in_db(params_to_update)
    
                
    def _is_automata_process_running(self):
        processes = get_processes('python')
        for process in processes:
            cmdline = ' '.join(process['cmdline'])
            if cmdline.endswith('python -m src'):
                return True
        return False
    
    
    def _recover_automata(self):
        self._delete_not_processed_data()
        self._start_automata()
        self._log_recovery()
        self._send_recovery_notification()
        
    
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
        
        
    def _start_automata(self):
        print('Starting automata...')
        try:
            subprocess.run(["./automata.sh"])
        except:
            print('Error while trying to start automata.')
            raise
            
            
    def _log_recovery(self):
        print('Logging recovery...')
        try:
            filepath = os.path.join('logs', 'schedule.log')
            with open(filepath, 'a+') as f:
                f.write(f'## SYSTEM RECOVERY AT {datetime.now()}')
                f.write('\n')
        except:
            print('Error while trying to log system recovery.')
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
    
    
    def _get_automata_status(self):
        try:
            with open('src/engine/status', 'r') as f:
                return int(f.read())
        except:
            print('Error while trying to send recovery notification.')
            raise
    
    
    def _stop_automata_process(self):
        print('Stopping automata process...')
        try:
            processes = get_processes('python')
            for process in processes:
                cmdline = ' '.join(process['cmdline'])
                if cmdline.endswith('python -m src'):
                    pid = process['pid']
                    subprocess.run(["kill", f'{pid}'])
        except:
            print('Error while trying to stop automata process.')
            raise
        
        
    def _log_params_update(self):
        print('Logging params update...')
        try:
            filepath = os.path.join('logs', 'schedule.log')
            with open(filepath, 'a+') as f:
                f.write(f'## PARAMS UPDATED AT {datetime.now()}')
                f.write('\n')
        except:
            print('Error while trying to log params update.')
            raise
    
    
    def _update_params_status_in_db(self, params_to_update):
        print('Updating params status in db...')
        try:
            params_ids = tuple([v[0] for v in params_to_update])
            self._dao.update_params_status_in_db(params_ids)
        except:
            print('Error while trying to update params status in db.')
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
        if self.engine_status == config.STATUS.RUNNING:
            self._logger.warning("Engine in processing. Impossible start a new one.")
        elif self.engine_status == config.STATUS.STOPPED:
            self.run_process()
        else:
            self._logger.error("Engine unavailable.")


    def run_process(self):
        try:
            self._logger.info('Running process...')
            self._set_status(config.STATUS.RUNNING)
            
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
            
            self._set_status(config.STATUS.STOPPED)
            self._logger.info('Process finished.')
        except:
            self._set_status(config.STATUS.ERROR)
            self._logger.critical('Engine in critical status.', exc_info=True)
            raise

    
    def _set_status(self, status):
        self.engine_status = status
        try:
            with open('src/engine/status', 'w') as f:
                f.write(str(status))
        except:
            self._logger.error('Error while trying to store status in disk.')
            raise
