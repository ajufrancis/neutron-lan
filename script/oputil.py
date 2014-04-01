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

    def mandatory(self, *args):

        for key in args:
            if key not in self.model.keys():
                return False
        return True


if __name__=='__main__':

    model = {
        'aaa': 1,
        'bbb': '2',
        'ccc': ['xxx', 'yyy']
        }

    m = Model(model)
    aaa, bbb, ccc, ddd = m.getparam('aaa', 'bbb', 'ccc', 'ddd')

    print aaa, bbb, ccc, ddd
   
    try:
        raise ModelError('TTTTTTTT')
    except Exception, e:
        print e

