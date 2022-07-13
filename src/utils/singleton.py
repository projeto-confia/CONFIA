from typing import Any


class SingletonMetaClass(type):
    """Creates a singleton object for the given class.

    Returns:
        InterventorDAO: the same singleton object if it has been already created. Otherwise, it creates a new one.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs) -> Any:
        
        if cls not in cls._instances:
            
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            
        return cls._instances[cls]