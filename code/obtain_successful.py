# %%
from datetime import datetime, timedelta
from pprint import pprint

from aiida import load_profile
from aiida.orm import *
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

load_profile()
# %%
qb = QueryBuilder()
# qb.append(, filters={"label": {"like": "eiger_test%"}}, tag="eiger")

time_threshold = datetime.now() - timedelta(days=30)

qb.append(
    SelfConsistentHubbardWorkChain,
    filters={
        "attributes.process_state": "finished",
        "attributes.exit_status": 0,
        "ctime": {">": time_threshold},
        "attributes.meta_convergence": Bool(True),
    },
    # tag="workchain",
)
qb.count()
successful_runs = qb.iterall()

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
# Finding the structures with the bandgap > 1.0.
qb = QueryBuilder()
qb.append(
    StructureData, tag="structure", project="*"
)  # Here we are projecting the entire structure object
qb.append(CalcJobNode, with_incoming="structure", tag="calculation")
qb.append(Dict, with_incoming="calculation", filters={"attributes.bandgap": {">": 1.0}})

# Adding the structures in 'promising_structures' group.
group = load_group(label="promising_structures")
group.add_nodes(q.all(flat=True))
