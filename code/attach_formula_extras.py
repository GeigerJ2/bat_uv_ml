# %%
from datetime import datetime, timedelta
from pprint import pprint

from aiida import load_profile
from aiida.orm import *
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

load_profile()

# %%

# ! .first should also return a list
# ! .iterall should also implement option `flat=True`


def attach_formula_extras(node_type, formula_mode: str = "hill"):

    qb = QueryBuilder()
    qb.append(node_type)

    for node in qb.all(flat=True):
        # print("Node:", node)
        if "formula_{}".format(formula_mode) not in node.extras.keys():
            formula = node.get_formula(mode=formula_mode)
            node.set_extra("formula_{}".format(formula_mode), formula)


attach_formula_extras(node_type=HubbardStructureData)

# %%
# sd_qb_filter = QueryBuilder()
# sd_qb_filter.append(
#     HubbardStructureData,
#     filters={"extras.keys": {"contains": "formula_hill"}},
#     #  project=['node', 'uuid', 'extras']
# )
# sd_qb_filter.count()

# extras =
# for uuid, extras in sd_qb.all():
#     if "_aiida_hash" not in extras:
#         sd_node = load_node()
#         print(uuid)

# sd_qb.count()
# print(sd_qb.first()[0])
# sd_devel = sd_qb.first()[0].get_formula()


# print(sd_devel)

# %% #? Debug with Francisco


qb = QueryBuilder()
_ = qb.append(HubbardStructureData)



for node in list(qb.iterall()):
    flat_node = node[0]
    print("flat_node:", flat_node)
    print(flat_node.extras)
    formula_hill = flat_node.get_formula()
    flat_node.set_extra('formula_hill', formula_hill)
    print(flat_node.extras)
    !verdi node extras 5213
    # flat_node.delete_extra('formula_hill')
    break

#%%
for node in qb.all():
    flat_node = node[0]
    print("flat_node:", flat_node)
    print(flat_node.extras)
    formula_hill = flat_node.get_formula()
    flat_node.set_extra('formula_hill', formula_hill)
    print(flat_node.extras)
    flat_node.delete_extra('formula_hill')
    !verdi node extras 5213

    break
