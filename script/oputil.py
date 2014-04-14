from env import NLAN_DIR 

class ModelError(Exception):

    def __init__(self, message):

        self.message = message

    def __str__(self):

        return self.message

class Model:

    def __init__(self, model):

        self.model = model

    def getparam(self, *args):
      
        for key in args:
            if key in self.model:
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

def get_roster():

    import os, yaml
    roster = os.path.join(NLAN_DIR,'roster.yaml')
    r = open(roster, 'r')
    return yaml.load(r.read())


if __name__=='__main__':

    print get_roster()

    model = {
        'aaa': 1,
        'bbb': '2',
        'ccc': ['xxx', 'yyy']
        }

    m = Model(model)
    aaa, bbb, ccc, ddd = m.getparam('aaa', 'bbb', 'ccc', 'ddd')

    try:
        raise ModelError('TTTTTTTT')
    except Exception, e:
        print e

