import json, sys; sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.sr_library_eml import run_session51
print(json.dumps(run_session51(), indent=2, default=str))
