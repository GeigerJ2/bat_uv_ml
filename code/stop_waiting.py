# %%
from datetime import datetime, timedelta

from aiida import load_profile
from aiida.orm import QueryBuilder, WorkChainNode
from aiida.orm.querybuilder import QueryBuilder
from aiida.plugins import CalculationFactory, DataFactory, WorkflowFactory
from aiida.tools.graph.deletions import delete_nodes
from aiida_quantumespresso.common.types import SpinType

PwCalculation = CalculationFactory("quantumespresso.pw")
load_profile()
# %%

qb = QueryBuilder()

ten_days_ago = datetime.now() - timedelta(days=10)

qb.append(
    WorkChainNode,
    filters={
        # "attributes.process_state": {"in": ["waiting", "excepted"]},
        "attributes.process_state": {"in": ["waiting", "excepted"]},
        "ctime": {
            "<": ten_days_ago
        },  # Filter processes with creation time older than 10 days ago
    },
    project=["id"],
)

node_ids = [result[0] for result in qb.all()]

print(len(node_ids))
# delete_nodes(node_ids, dry_run=True)

# %%
