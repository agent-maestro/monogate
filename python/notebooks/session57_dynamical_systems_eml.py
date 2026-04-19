import json,sys; sys.path.insert(0,"D:/monogate/python")
from monogate.frontiers.dynamical_systems_eml import run_session57
print(json.dumps(run_session57(),indent=2,default=str))
