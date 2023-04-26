# %%
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import importlib
import json
import os
from pathlib import Path
from pprint import pprint

import pandas as pd
import pyconfsamp.core
from aiida import load_profile
from aiida.engine import submit
from aiida.orm import (
    Bool,
    Group,
    Int,
    Str,
    StructureData,
    load_code,
    load_group,
    load_node,
)
from aiida.orm.nodes.data.array.kpoints import KpointsData
from aiida_quantumespresso.common.types import SpinType
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase import Atoms
from ase.visualize import view
from project_data import (
    DEFAULT_BUILDER_DICT,
    GLOBAL_SYMPREC,
    HUBBARD_DICT,
    SORTING_DICT,
)
from project_functions import run_full_sampling
from pybat import Cathode
from pybat.core import Cathode
from pyconfsamp.core import change_atom_names_same_symbol
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor

# from aiida.orm import UpfData, UpfFamily

load_profile()


# %% #? Read in df of fully lithiated structures

# ! Instead of using pandas df and pickle, directly store the node as StructureData in AiiDA
fully_lithiated_df = pd.read_pickle(
    os.path.join("..", "data", "fully_lithiated_df.pkl")
)
print(fully_lithiated_df.shape)
fully_lithiated_df.head()

lfpo_ase_structure = fully_lithiated_df["ase_in"].values[0]
lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[1]
lmpo_ase_structure = fully_lithiated_df["ase_in"].values[2]

# %% #? Submit lmpo at option 3

# lmpo_submission = run_full_sampling(
#     ase_structure=lmpo_ase_structure,
#     short_name="lmpo",
#     cell_size=1,
#     relax_option=3,
#     group_label="eiger_test/lmpo-1/option3/fm",
#     submit_index=0,
# )
# %% #? Submit lfpo at option 3

lfpo_submission = run_full_sampling(
    ase_structure=lfpo_ase_structure,
    short_name="lfpo",
    cell_size=1,
    relax_option=3,
    group_label="eiger/lfpo-1/option3/fm",
    submit_index=0,
)

# %% #? Submit lfmpo

lfmpo_submission = run_full_sampling(
    ase_structure=lfmpo_ase_structure,
    short_name="lfmpo",
    cell_size=1,
    relax_option=3,
    group_label="eiger_test/lfmpo-1/option3/fm",
    submit_index=0,
)

# %%
