# %%
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import os
from pathlib import Path

import pandas as pd
from aiida import load_profile
from aiida.orm import load_node
from project_data import DEFAULT_BUILDER_DICT
from project_functions import run_full_sampling

# from aiida.orm import UpfData, UpfFamily

load_profile()


# %% #? Read in df of fully lithiated structures

# ! Instead of using pandas df and pickle, directly store the node as StructureData in AiiDA
# fully_lithiated_df = pd.read_pickle(
#     os.path.join("..", "data", "fully_lithiated_df.pkl")
# )
# print(fully_lithiated_df.shape)
# fully_lithiated_df.head()

# lfpo_ase_structure = fully_lithiated_df["ase_in"].values[0]
# lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[1]
# lmpo_ase_structure = fully_lithiated_df["ase_in"].values[2]


# %% #? Submit lfmpo with the hopefully working settings.

builder_dict = dict(DEFAULT_BUILDER_DICT)
builder_dict["overrides"] = Path(
    os.path.join("yaml_files", "low_thresh_overrides.yaml")
)

pk_list = [58659, 58660, 58661, 58662, 58663]
name_list = ["lfpo", "lfmpo", "lmpo", "lmno", "lmo"]

print(DEFAULT_BUILDER_DICT)

for name, pk in list(zip(name_list, pk_list)):
    if name in ["lfpo", "lfmpo", "lmpo"]:
        for option in [3]:
            lfmpo_submission = run_full_sampling(
                ase_structure=load_node(pk).get_ase(),
                short_name=name,
                cell_size=1,
                relax_option=option,
                group_label="lower_thresh/{}-1/option{}/fm".format(name, option),
                builder_dict=builder_dict,
            )
