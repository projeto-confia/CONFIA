import logging
from src.config import Config as config
from src.interventor.interventor import Interventor, InterventorManager


class InterventorFacade(object):
    """
    docstring
    """

    def __init__(self):
        self._logger = logging.getLogger(config.LOGGING.NAME)


    async def run(self):
        try:
            self._logger.info('Running Interventor...')
            await Interventor().run()
            self._logger.info('Interventor finished.')
        except:
            raise
        
        
    # def run_manager(self):
    #     InterventorManager().run()
