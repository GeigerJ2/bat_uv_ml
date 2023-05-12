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

def pks_by_label(label):
    qb = QueryBuilder()

    qb.append(
        SelfConsistentHubbardWorkChain,
        filters={
            "label": {"like": "%{}%".format(label)},
            #     "attributes.process_state": "finished",
            #     "attributes.exit_status": 0,
            #     "ctime": {">": time_threshold},
        },
        # tag="workchain",
        project="*",
    )

    print("Count: {}".format(qb.count()))
    qb_all = qb.all(flat=True)

    return [_.pk for _ in qb_all]



docc_thr_skip_first = pks_by_label(label="docc_thr_skip_first")

#%%

for pk in docc_thr_skip_first:
    !verdi process status $pk

#%%

iurii_wcs = pks_by_label(label="iurii")

for pk in iurii_wcs:
    print(pk)
    !verdi process status $pk
    print('='*100)
