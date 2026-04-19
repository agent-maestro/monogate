import json,sys; sys.path.insert(0,"D:/monogate/python")
from monogate.frontiers.euler_product_eml import run_session58
print(json.dumps(run_session58(),indent=2,default=str))
