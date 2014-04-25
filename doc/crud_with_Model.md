CRUD with Model object
======================
2014/4/25

<pre>
from oputil import Model
m = Model(operation, model, index)
</pre>

Then the function automatically generates the following variables in the global name space.

<pre>
_param1, _para2, _para3...        (1) 
_param1_, _param2_, _param3_...   (2)
param_, param2_, param3_... (3)
</pre>

(1) from NLAN Master -- new values 
(2) either from NLAN Master or from OVSDB -- if not new values then old values
(3) from OVSDB -- old values

state -+- param a
       |
       +- param b
       |
       +- param c
       |
       +- param d

NLAN                  --- generated variables ---
state  (Req)  (OVSDB)  (new)  (new/old)  (old)
params  new     old   _param   _param_   param_
-------------------------------------------------
a        1      None   _a=1     _a_=1    a_=None
b        1       1     _b=1     _b_=1    b_=1
c      None      1     _c=None  _c_=1    c_=1
d      None     None   _d=None  _d_=None d_=None
</pre>
  
* _param: representes desired state including the values sent from NLAN Master in a NLAN Request (includes diff-values only)
* _param_: represents desired state including all the other exisiting values in OVSDB
* param_: representes existing state including all the values in OVSDB 

Treat them like 'final' variables in Java: never change the values in the module.
To finalize the process, call the following function to save the parameters in OVSDB:
<pre>
m.finalize()
</pre>

