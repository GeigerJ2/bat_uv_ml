# %%
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import importlib
import os

import pandas as pd
import pyconfsamp.core
from aiida import load_profile
from aiida.orm import StructureData
from ase import Atoms
from project_data import (
    DEFAULT_BUILDER_DICT,
    GLOBAL_SYMPREC,
    HUBBARD_DICT,
    SORTING_DICT,
)
from project_functions import run_full_sampling, view_structure_from_pk

# from aiida.orm import UpfData, UpfFamily

load_profile()


# %% #? Read in df of fully lithiated structures

# ! Instead of using pandas df and pickle, directly store the node as StructureData in AiiDA
fully_lithiated_df = pd.read_pickle(
    os.path.join("..", "data", "fully_lithiated_df.pkl")
)
print(fully_lithiated_df.shape)
fully_lithiated_df.head(100)

# lfpo_ase_structure = fully_lithiated_df["ase_in"].values[0]
# lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[1]
# lmpo_ase_structure = fully_lithiated_df["ase_in"].values[2]
lmno_ase_structure = fully_lithiated_df["ase_in"].values[3]
lmo_ase_structure = fully_lithiated_df["ase_in"].values[4]

# %% #? Submit lfpo

for option in (1, 2, 3):
    # ? Submit lmno
    lfpo_submission = run_full_sampling(
        ase_structure=lmno_ase_structure,
        short_name="lmno",
        cell_size=1,
        relax_option=3,
        group_label="eiger_test/lmno-1/option{}/fm".format(option),
        submit_index=0,
    )

    # ? Submit lmo
    lfmpo_submission = run_full_sampling(
        ase_structure=lmo_ase_structure,
        short_name="lmo",
        cell_size=1,
        relax_option=3,
        group_label="eiger_test/lmo-1/option{}/fm".format(option),
        submit_index=0,
    )

# %%
