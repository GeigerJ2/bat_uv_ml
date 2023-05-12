# %%
from datetime import datetime, timedelta

from aiida import load_profile
from aiida.orm import QueryBuilder
from aiida.plugins import CalculationFactory, DataFactory, WorkflowFactory
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from project_data import *

HubbardStructureData = DataFactory("quantumespresso.hubbard_structure")
PwRelaxWorkChain = WorkflowFactory("quantumespresso.pw.relax")
PwBaseWorkChain = WorkflowFactory("quantumespresso.pw.base")
PwCalculation = CalculationFactory("quantumespresso.pw")

load_profile()

# %%


time_threshold = datetime.now() - timedelta(days=10)
qb = QueryBuilder()

qb.append(
    SelfConsistentHubbardWorkChain,
    filters={
        "attributes.process_state": "finished",
        "attributes.exit_status": 402,
        "ctime": {">": time_threshold},
        # "attributes.meta_convergence": Bool(True),
        # "attributes.meta_convergence": "False",
    },
    tag="scf_402",
)

qb.append(
    PwRelaxWorkChain,
    filters={"attributes.exit_status": 401},
    with_incoming="scf_402",
    tag="relax",
)

qb.append(
    PwBaseWorkChain,
    filters={"attributes.exit_status": 401},
    with_incoming="relax",
    tag="pw_base",
)

qb.append(
    PwCalculation,
    filters={"attributes.exit_status": 520},
    with_incoming="pw_base",
    tag="pw_calc",
)

qb.count()
for calc in qb.iterall():
    print(calc[0].pk)


# %%
