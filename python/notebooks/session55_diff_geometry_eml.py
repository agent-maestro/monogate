import json,sys; sys.path.insert(0,"D:/monogate/python")
from monogate.frontiers.diff_geometry_eml import run_session55
print(json.dumps(run_session55(),indent=2,default=str))
