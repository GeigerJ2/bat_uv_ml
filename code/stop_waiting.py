# %%
from aiida import load_profile
from aiida.orm import CalcJobNode, Computer, Group, QueryBuilder
from aiida.plugins import CalculationFactory, DataFactory, WorkflowFactory
from aiida_quantumespresso.common.types import SpinType

PwCalculation = CalculationFactory("quantumespresso.pw")
load_profile()
# %%

qb = QueryBuilder()

qb.append(
    Computer,
    filters={"label": "%lumi%"},
    tag="lumi",
)

qb.append(
    CalcJobNode,
    filters={"attributes.process_state": "waiting"},
    tag="wait",
    with_computer="lumi",
)

qb.all()

# %%
