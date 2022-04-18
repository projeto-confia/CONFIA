from src.interventor.facade import InterventorFacade


class Schedule(object):
    
    def __init__(self):
        print('Starting schedule...')
        
        
    def run(self):
        InterventorFacade().run_manager()


if __name__ == '__main__':
    Schedule().run()
