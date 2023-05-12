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

ERROR_SUB_PROCESS_FAILED_RELAX = 402
ERROR_SUB_PROCESS_FAILED_SCF = 403
ERROR_SUB_PROCESS_FAILED_HP = 404


qb = QueryBuilder()

qb.append(
    SelfConsistentHubbardWorkChain,
    filters={
        "attributes.exit_status": 0,
    },
    project="*",
)

print("Count: {}".format(qb.count()))
qb_all = qb.all(flat=True)

# return [_.pk for _ in qb_all]


def query_failed_wc(wc_node, exit_status):
    qb = QueryBuilder()

    qb.append(
        SelfConsistentHubbardWorkChain,
        filters={"attributes.exit_status": exit_status},
        project="*",
        tag="workchain",
    )

    qb.count()
    return qb.iterall()


# qb_test2.count()
# qb_test.all()[0]

query_404 = query_failed_wc(
    wc_node=SelfConsistentHubbardWorkChain, exit_status=ERROR_SUB_PROCESS_FAILED_HP
)
