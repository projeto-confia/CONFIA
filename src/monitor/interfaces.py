import abc


class CollectorInterface(metaclass=abc.ABCMeta):
    """Interface to collectors
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'run') and
                callable(subclass.run) and
                hasattr(subclass, '_get_data') and
                callable(subclass._get_data) and
                hasattr(subclass, '_process_data') and
                callable(subclass._process_data) and
                hasattr(subclass, '_persist_data') and
                callable(subclass._persist_data) or
                NotImplemented)
        

    @abc.abstractmethod
    def run(self):
        """
        Execute main methods get, process, persist
        """
        raise NotImplementedError
    

    @abc.abstractmethod
    def _get_data(self):
        """
        Get data from social network.
        """
        raise NotImplementedError


    @abc.abstractmethod
    def _process_data(self):
        """
        Process data collected from social network.
        """
        raise NotImplementedError


    @abc.abstractmethod
    def _persist_data(self):
        """
        Persist data processed into database.
        """
        raise NotImplementedError


class TwitterStatusProcessorInterface(metaclass=abc.ABCMeta):
    """Interface to TwitterStatusProcessor
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'process') and
                callable(subclass.process) or
                NotImplemented)
        

    @abc.abstractmethod
    def process(self, status):
        """
        Process status
        """
        raise NotImplementedError
