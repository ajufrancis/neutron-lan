# 2014/4/25, Model class
#
from ovsdb import Row
import inspect

class Model:

    # This constructor automatically generates state variables:
    # _param, _param_ and param_
    def __init__(self, operation, model, index=None):

        self.operation = operation
        self.model = model
        self.index = index
        # Gets a caller's module name from a frame object
        cf = inspect.currentframe()
        of = inspect.getouterframes(cf)
        self.gl = of[1][0].f_globals
        self.module = self.gl['__name__'] 
        # Get the current state from OVSDB
        self.rowobj = Row(self.module, index)
        self.row = self.rowobj.getrow()
        # Generates state variables
        self._get_all()

    def getparam(self, *args):
      
        for key in args:
            if key in self.model:
                if self.model[key] == '':
                    yield None
                else:
                    yield self.model[key]
            else:
                yield None

    def getparams(self, *args):

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
            if key in self.row:
                self.gl[key_] = self.row[key]
            else:
                self.gl[key_] = None 
            # New or Old values
            _key_ = '_'+key+'_'
            if self.gl[_key] == None:
                # from old value
                self.gl[_key_] = self.gl[key_]
            else:
                # from new value
                self.gl[_key_] = self.gl[_key]
            
    
    def _get_all(self):
        params = tuple(__n__['types'][self.module].keys())
        self.getparams(*params)


    # ovdsb.Row.crud
    def finalize(self):
        self.rowobj.crud(self.operation, self.model)


    # args: a set of mandatory parameters
    def checkset(self, module, crud, args):

        a = sets.Set(args)
        b = sets.Set(self.model.keys())
        if len(a - b) == 0 or len(a & c) == 0:
            pass 
        else:
            raise ModelError(module + "." + crud + " requires" +  str(args), "or all None")


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


if __name__=='__main__':

    #print get_roster()

    model = {
        'aaa': 1,
        'bbb': '2',
        'ccc': ['xxx', 'yyy']
        }

    m = Model(model)
    aaa, bbb, ccc, ddd = m.getparam('aaa', 'bbb', 'ccc', 'ddd')

    try:
        raise ModelError('Something is wrong')
    except Exception, e:
        print e

    try:
        raise ModelError('Model is wrong', model)
    except Exception as e:
        print e
        print e.model

    try:
        raise ModelError('Param is wrong', model, 'aaa')
    except Exception as e:
        print e
        print e.model
        print e.params

    try:
        raise ModelError('Params is wrong', None, ['aaa', 'bbb'])
    except Exception as e:
        print e
        print e.model
        print e.params