import psutil


def get_processes(process_name):
    '''
    Get a list of all the PIDs of a all the running process whose name contains
    the given string process_name
    '''
    processes = []
    #Iterate over the all the running process
    for process in psutil.process_iter():
       try:
           pinfo = process.as_dict(attrs=['pid', 'name', 'create_time', 'cmdline'])
           # Check if process name contains the given name string.
           if process_name.lower() in pinfo['name'].lower():
               processes.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess):
           pass
    return processes
