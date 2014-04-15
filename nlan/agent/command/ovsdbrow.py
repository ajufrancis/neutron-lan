from ovsdb import OvsdbRow

def getrow(*args):
    table = args[0]
    index = None
    if len(args) > 1:
        index = (args[1], eval(args[2]))
    row = OvsdbRow(table, index)
    return row.getrow()
