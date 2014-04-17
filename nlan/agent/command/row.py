import ovsdb

Row = ovsdb.Row

def getrow(*args):
    module = args[0]
    index = None
    if len(args) > 1:
        index = (args[1], eval(args[2]))
    row = Row(module, index)
    return row.getrow()

def get_current_state():

    return ovsdb.get_current_state()
