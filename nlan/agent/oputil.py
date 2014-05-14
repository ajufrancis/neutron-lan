# 2014/4/25, Model class
#
from ovsdb import Row
import inspect

class Model:

    # This constructor automatically generates state variables:
    # _param, _param_ and param_
    def __init__(self, operation, module, model, index=None):

        self.operation = operation
        self.model = model
        self.index = index
        self.module = module 
        # Get the current state from OVSDB
        self.rowobj = Row(self.module, index)
        self.row = self.rowobj.getrow()

    def getparam(self, *args):
      
        for key in args:
            if key in self.model:
                if self.model[key] == '':
                    yield None
                else:
                    yield self.model[key]
            else:
                yield None

    def _params(self, *args):
       
        init = False
        if __n__['init'] == 'start':
            init = True

        for key in args:

            # New values
            _key = '_'+key
            if key in self.model:
                if self.model[key] == '':
                    self.gl[_key] = None
                else:
                    self.gl[_key] = self.model[key] 
            else:
                self.gl[_key] = None 
            # Old values stored in OVSDB            
            key_ = key+'_'
            if key in self.row and not init:
                self.gl[key_] = self.row[key]
            else: # including __n__['init'] == 'start'
                self.gl[key_] = None 
            # New or Old values
            _key_ = '_'+key+'_'
            if self.gl[_key] == None:
                # Desired state: old value
                self.gl[_key_] = self.gl[key_]
            else:
                if self.operation == 'add' or self.operation == 'update':
                    # Desired state: new value
                    self.gl[_key_] = self.gl[_key]
                else:  # 'delete'
                    # Desierd state: None
                    self.gl[_key_] = None 
    
    def params(self):
        
        cf = inspect.currentframe()
        of = inspect.getouterframes(cf)
        self.gl = of[1][0].f_globals

        params = tuple(__n__['types'][self.module].keys())
        self._params(*params)


    # ovdsb.Row.crud
    def finalize(self):
        self.rowobj.crud(self.operation, self.model)


class SubprocessError(Exception):

    def __init__(self, message, command=None):

        self.message = message
        self.model = command 

    def __str__(self):

        message = '' 
        if self.command:
            message = "{}\ncommand:{}".format(self.message, self.command)
        else:
            message = self.message

        return message


def logstr(*args):

    l = list(args)
    return '\n'.join(l)

# Converts command arguments into a model
def parse_args(module, *args):

    schema = __n__['types'][module]
    
    def _type(key):
        
        if 'value' in schema[key]: # dict
            type_ = schema[key]['value']['type']
            if type_ == 'string':
                return (dict, str)
            elif type_ == 'integer':
                return (dict, int)
            else:
                return None
        else:
            type_ = schema[key]['key']['type']
            t = None
            if type_ == 'string':
                t = str 
            elif type_ == 'integer':
                t = int
            if int(schema[key]['max']) > 1:  # list
                return (list, t)
            else:
                return (None, t)

    model = {}

    for s in args:
        ss = s.split('=')
        k = s[0]
        v = s[1]
        t = _type(k)
        if t[0] == None:
            value = t[1](v)
            model[k] = value
        elif t[0] == dict:
            value = {}
            for item in v.split(','):
                pair = item.split(':')
                value[pair[0]] = t[1](pair[1])
            model[k] = value
        elif t[0] == list:
            value = []
            for item in v.split(','):
                value.append(t[1](item))
            model[k] = value

    return model
                

