import threading
import logging
from src.monitor.facade import MonitorFacade
from src.detection.facade import DetectorFacade
from src.scraping.facade import ScrapingFacade
from src.fcmanager.facade import FactCheckManagerFacade
from src.interventor.facade import InterventorFacade
from src.config import Config as config
from src.engine.dao import EngineDAO


class EngineManager(object):
    
    def __init__(self) -> None:
        self._dao = EngineDAO()
        # self._logger = logging.getLogger()

    
    def run(self):
        print('Running Engine Manager...')
        # 1) Verificar se o processo do automata está em execução no S.O.
        # 2) Caso negativo:
            # Remover dados não processados (diretório data)
            # Backup do arquivo nohup.out
            # Iniciar o processo do automata no S.O. 
            # Disparar notificação
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
