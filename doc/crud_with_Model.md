import oputil
m = oputil.Model(globals(), module, model, index)
m.get_all()

Then the function automatically generates the following variables in the global name space.

param1, para2, para3...        (1) 
param1_, param2_, param3_...   (2)
param__, param2__, param3__... (3)

(1) from NLAN Master -- new values 
(2) either from NLAN Master or from OVSDB -- if not new values then old values
(3) from OVSDB -- old values

Treat them like 'final' variables in Java: never change the values in the module.
To finalize the process, call the following function to save the parameters in OVSDB:
m.crud(crud, model)

or m.add(model), m.update(model), m.delete(model)

