from datetime import datetime
import re


class ConfigBuilder(object):
    
    def __init__(self) -> None:
        self.filepath = 'src/config.py'
        self.params_to_update = dict()
        self.fileheader = ''
        self.filebody = ''
    

    def build(self, params_to_update=None):
        if not params_to_update:
            return
        self._parse_params_to_update(params_to_update)
        self._build_body()
        self._build_header()
        self._write_content()
    
    
    def _parse_params_to_update(self, params_to_update):
        for param in params_to_update:
            id, name, type, value = param
            module, attr = name.split('.')
            attr_dict = {attr: {'id': id, 'type': type, 'value': value}}
            if module in self.params_to_update.keys():
                self.params_to_update[module].update(attr_dict)
            else:
                self.params_to_update[module] = attr_dict
    
    
    def _build_header(self):
        self.fileheader += f'# Created at {datetime.now()}'
        self.fileheader += '\n\n'


    def _build_body(self):
        class_pattern = re.compile('\s+class\s+(\w+)\(')
        attr_pattern = re.compile('\s+(\w+)\s+=\s+(.*)')
        with open('src/config.py', 'r') as f:
            current_class = None
            while line := f.readline():
                class_match = re.search(class_pattern, line)
                if class_match:
                    current_class = class_match.group(1)
                if current_class in self.params_to_update.keys():
                    attr_match = re.search(attr_pattern, line)
                    if attr_match and attr_match.group(1) in self.params_to_update[current_class].keys():
                        prefix = line.split('=')[0]
                        value = self._parse_value(self.params_to_update[current_class][attr_match.group(1)])
                        line = prefix + ' = ' + value + ' ####### MODIFIED' + '\n'
                self.filebody += line
    
    
    def _parse_value(self, param):
        value = param['value']
        if param['type'] == 'string':
            return f'"{value}"'
        if param['type'] == 'array[string]':
            return str(value.split(';'))
        return value
    
    
    def _write_content(self):
        with open(self.filepath, 'w') as f:
            f.write(self.fileheader)
            f.write(self.filebody)
