
class ModelError(Exception):

    def __init__(self, message, model=None, params=None):

        self.message = message
        self.model = model
        self.params = params

    def __str__(self):

        if self.model and self.params:
            message = "Model error: {}\nmodel:{}\nparams:{}".format(self.message, str(self.model), str(self.params))
        elif self.model:
            message = "Model error: {}\nmodel:{}".format(self.message, str(self.model))
        elif self.params:
            message = "Model error: {}\nparams:{}".format(self.message, str(self.params))
        else:
            message = "Model error: {}".format(self.message)

        return message

class Model:

    def __init__(self, model):

        self.model = model

    def getparam(self, *args):
      
        for key in args:
            if key in self.model:
                if self.model[key] == '':
                    yield None
                else:
                    yield self.model[key]
            else:
                yield None

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

def get_roster():

    from env import NLAN_DIR 
    import os, yaml
    roster = os.path.join(NLAN_DIR,'roster.yaml')
    r = open(roster, 'r')
    return yaml.load(r.read())

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
