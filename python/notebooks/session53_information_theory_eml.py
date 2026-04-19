import json,sys; sys.path.insert(0,"D:/monogate/python")
from monogate.frontiers.information_theory_eml import run_session53
print(json.dumps(run_session53(),indent=2,default=str))
