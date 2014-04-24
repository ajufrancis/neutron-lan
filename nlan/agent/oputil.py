from ovsdb import Row

class Model:


    def __init__(self, gl, module, model, index=None):

        self.model = model
        self.module = module
        self.index = index
        self.gl = gl
        self.rowobj = Row(module, index)
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

    def getparams(self, *args):

        for key in args:

            # New values
            if key in self.model:
                if self.model[key] == '':
                    self.gl[key] = None
                else:
                    self.gl[key] = self.model[key] 
            else:
                self.gl[key] = None 
            # Old values stored in OVSDB            
            key__ = key+'__'
            if key in self.row:
                self.gl[key__] = self.row[key]
            else:
                self.gl[key__] = None 
            # New or Old values
            key_ = key+'_'
            if self.gl[key] == None:
                self.gl[key_] = self.gl[key__]
            else:
                self.gl[key_] = self.gl[key]
            
    
    def get_all(self):

        params = tuple(__n__['types'][self.module].keys())
        self.getparams(*params)

    # ovdsb.Row.crud
    def crud(self, crud, model):
        self.rowobj.crud(crud, model)

    # ovdsb.Row.add
    def add(self, model):
        self.rowobj.crud('add', model)

    # ovdsb.Row.update
    def update(self, model):
        self.rowobj.crud('update', model)

    # ovdsb.Row.delete
    def delete(self, model):
        self.rowobj.crud('delete', model)

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
