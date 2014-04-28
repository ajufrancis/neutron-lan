CRUD with Model object
======================
2014/4/25

In a NLAN config module,
<pre>
def add(model):
    model.params()
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
    model.finalize()
</pre>


Rollback mechanism (just an idea)
---------------------------------
2014/4/28

I made an experiment on "subnets.py" as an example, following the idea above, and after having wrote some scripts, I found that the CRUD operations in the script seemed like OpenFlow entries:
- It is basically a list of add/delete commands.
- If some match condition is satisfied, then CRUD operation(s) are performed. Repeat that until the bottom of the command entries.

Basic rule of match condition:

For add,
  if _parm:
      command _param_

For delete,
  if _param:
      command param_

Create a Command entries mimicing OpenFlow table:

Table 0
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
Table 1
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
Table 2
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
<idx><match><add_command><add_params><del_command><del_params><resubmit><prev_idx>
                           :

The table is dynamically created when add/delete/update operation is called.

If the command executions fails at some point, then a rollback procedure takes over:
- Revert the execution order
- In case of add failure, del upwards following prev_idx.
- In case of del failure, add upwards following prev_idx.

Every entry is executed in try: and except:

try:
   add/del_command add/del_params
except:
   rollback(idx)


