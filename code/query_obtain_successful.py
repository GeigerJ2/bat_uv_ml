# %%
from datetime import datetime, timedelta
from pprint import pprint

from aiida import load_profile
from aiida.orm import *
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from aiida_quantumespresso.workflows
from aiida_vasp.workchains.converge import ConvergeWorkChain
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

load_profile()
# %%
qb_success = QueryBuilder()
# qb.append(, filters={"label": {"like": "eiger_test%"}}, tag="eiger")

time_threshold = datetime.now() - timedelta(days=30)

qb_success.append(
    SelfConsistentHubbardWorkChain,
    filters={
        "attributes.process_state": "finished",
        "attributes.exit_status": 0,
        "ctime": {">": time_threshold},
    },
    tag="workchain",
)

print("Count: {}".format(qb_success.count()))
qb_success_all = qb_success.all()

# %% #? Filter successful workchains by meta_convergence = True

true_meta_convergences = []
for success_wc in qb_success.all(flat=True):
    meta_convergence = success_wc.inputs.meta_convergence.value
    if meta_convergence is True:
        true_meta_convergences.append(success_wc.pk)

true_meta_convergences = sorted(true_meta_convergences)

# %% #?
for true_meta_convergence in true_meta_convergences:
    print(true_meta_convergence)


# %%

qb_edge_filter = QueryBuilder()
# qb.append(, filters={"label": {"like": "eiger_test%"}}, tag="eiger")

time_threshold = datetime.now() - timedelta(days=30)

qb_edge_filter.append(
    SelfConsistentHubbardWorkChain,
    filters={
        "attributes.process_state": "finished",
        "attributes.exit_status": 0,
        "ctime": {">": time_threshold},
    },
    tag="workchain",
    project="*",
)

qb_edge_filter.append(
    Bool,
    filters={"attributes.value": True},
    with_outgoing="workchain",
    edge_filters={"label": "meta_convergence"},
)

print("Count: {}".format(qb_edge_filter.count()))
# qb_success_all = qb_edge_filter.all()
qb_edge_filters = qb_edge_filter.all(flat=True)
print(qb_edge_filters[0])
for qb_edge_filter in qb_edge_filters:
    print(qb_edge_filter.inputs.meta_convergence.value)

# %%
# from aiida import orm
# from aiida.orm.querybuilder import QueryBuilder

# qb = QueryBuilder()

# # Define the main node class to search for
# qb.append(orm.Dict, tag="parameters")

# # Add filters to find nodes with the 'meta_convergence' key and a value of True
# qb.add_filter("parameters", {"attributes.meta_convergence": {"==": True}})

# # Retrieve the results
# results = qb.count()
# print(results)


# %%
final_pks = []
ase_structures = []

for successful_run in successful_runs:
    scf_dict = successful_run[0].inputs.scf.pw.parameters.get_dict()
    ase_structure = successful_run[0].inputs.hubbard_structure.get_ase()
    meta_convergence = successful_run[0].inputs.meta_convergence.value
    # print(meta_convergence)
    symbols = ase_structure.get_chemical_formula()
    if (
        "nspin" in scf_dict["SYSTEM"].keys()
        and "P" in symbols
        and meta_convergence is True
    ):
        final_pks.append(successful_run[0].pk)
        ase_structures.append(ase_structure)

# print(final_pks)
# view(ase_structures)
# print(ase_structures)

# %%

mykind = {'mass': 51.9961, 'name': 'Cr', 'symbols': ['Cr'], 'weights': [1.0]}

qb = QueryBuilder()

qb.append(
    WorkChainNode,
    # WorkChainNode,
    filters={"attributes.process_state": "finished", "attributes.exit_status": 0},
    tag="converge_wc",
    project="*",
)
qb.append(
    StructureData,
    with_incoming="converge_wc",
    filters={
        "attributes.kinds": {'contains': [mykind]},
    },
)
for wc_node in qb.all(flat=True):
    if 'structure' in wc_node.inputs:
        print(wc_node)
        wc_node.inputs.structure.attributes["kinds"]
        break


# %%
