# %%
from pprint import pprint

from aiida import load_profile
from aiida.orm import Group, QueryBuilder, load_group, load_node
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

load_profile()
# %%
qb = QueryBuilder()
qb.append(Group, filters={"label": {"like": "eiger_test%"}}, tag="eiger")
qb.append(SelfConsistentHubbardWorkChain, with_group="eiger")
qb.count()
eiger_test_runs = qb.all()
# pprint(eiger_test_runs)
test_run = eiger_test_runs[0][0]
test_run

for eiger_run in eiger_test_runs:
    print(eiger_run[0].exit_status)

# %%
