import json,sys; sys.path.insert(0,"D:/monogate/python")
from monogate.frontiers.generating_fn_eml import run_session56
print(json.dumps(run_session56(),indent=2,default=str))
