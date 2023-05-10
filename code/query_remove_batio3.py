# %%
from datetime import datetime, timedelta
from pprint import pprint

from aiida import load_profile
from aiida.orm import *
from aiida.tools.graph.deletions import delete_nodes
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

load_profile()
# %%

qb_batio3 = QueryBuilder()

qb_batio3.append(
    SelfConsistentHubbardWorkChain,
    filters={
        "attributes.process_state": "finished",
        "attributes.exit_status": 0,
    },
    tag="workchain",
    project="*",
)

qb_batio3.append(
    HubbardStructureData,
    with_outgoing="workchain",
    # filters={"attributes.sites.kind_name": {"contains": "Ba"}},
)

batio3_wc_list = []

for wc in qb_batio3.all(flat=True):
    hubbard_structure = wc.inputs.hubbard_structure
    if "Ba" in hubbard_structure.get_formula():
        batio3_wc_list.append(wc.pk)

# %%
# print(len(batio3_wc_list))
print(batio3_wc_list)
#     # print(type(wc))
#     print(wc.pk)
#     print(wc.get_formula())
#     # sd.get_formula()
#     # print(wc)
#     break
# delete_nodes(batio3_wc_list, dry_run=True)
