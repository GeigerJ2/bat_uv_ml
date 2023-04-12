# %% # ? Imports
import importlib
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pyconfsamp.core
from aiida import load_profile
from aiida.orm import Group, load_code, load_group, load_node
from aiida_quantumespresso.common.types import SpinType
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

pd.set_option('display.max_rows', None)
InteractiveShell.ast_node_interactivity = "all"
# %% # ? Loading stuff, structures, settings, etc.

# ? Where to move global variables ideally?
GLOBAL_SYMPREC = 1e-5
CELL_SIZE = 1
OPTION = 3

load_profile()

pw_code = load_code(2182)
hp_code = load_code(2183)

structure_data_pks = [7209, 7210, 7211, 7212, 7213]
structure_datas = [
    load_node(structure_data_pk) for structure_data_pk in structure_data_pks
]

fully_lithiated_names = [
    "LFPO",
    "LFMPO",
    "LMPO",
    "LMNO",
    "LMO",
]  # 3 x olivine, 2 x spinels

RELABEL_DICT = {
    0: "Mn0",
    1: "Mn0",
    2: "Mn1",
    3: "Mn1",
}

# MAG_DICT used when AFM magnetic ordering should be used
MAG_DICT = {
    "starting_magnetization": {
        "Mn0": 0.5,
        "Mn1": -0.5,
        # ? The following ones could be set via dict.get(default: 0.0)
        "O": 0.0,
        "P": 0.0,
        "Li": 0.0,
    },
    # "nspin": 2,
}

CONFIG_DICT = {
    "cation_list": ["Li", "Vac"],
    "concentration_restrictions": {"Li": (0, 1)},
    "max_configurations": None,
    "symprec": GLOBAL_SYMPREC,
}

HUBBARD_DICT = {
    "Mn": ("3d", 5.6),  # ? Average between 4.6 and 6.6
    "Fe": ("3d", 5.3),
    "Ni": ("3d", 8.6),
}

BUILDER_DICT = {
    "pw_code": pw_code,
    "hp_code": hp_code,
    "protocol": "moderate",
    "overrides": Path(os.path.join("yaml_files", "default_overrides.yaml")),
    "spin_type": SpinType.COLLINEAR,
}

SHOW_COLUMNS = [
    "short_name",
    "cell_size",
    "li_number",
    "formula",
    "space_group",
    "ion_concentration",
    "config_index",
    "li_mpc",
    "cell_mpc",
    "sg_mpc",
    "specific_name",
]

df_dict = {}

for short_name, structure_data in zip(fully_lithiated_names, structure_datas):
    for cell_size in [1, 2]:
        file_name = "testing_{}_{}_{}".format(short_name, cell_size, OPTION)
        try:
            class_object = pd.read_pickle(
                "/home/jgeiger/projects/bat_uv_ml/data/{}.pkl".format(file_name)
            )

            object_df = class_object.data_df()
            # object_df[SHOW_COLUMNS].head(1000)
            df_dict[file_name] = object_df

        except:
            pass

#%%

for df_name, df in df_dict.items():
    print(df_name, df.shape)



# %% # ?

print(list(df_dict.keys()))

# px.histogram(df_dict['testing_LMPO_1_3'], x='ion_concentration', y='li_mpc', name='li_mpc')

devel_df = df_dict["testing_LMPO_2_3"]
devel_df[SHOW_COLUMNS].sort_values(by=["ion_concentration"]).

# fig = go.Figure()
# _ = fig.add_trace(
#     go.Histogram(
#         x=devel_df["ion_concentration"],
#         y=devel_df["li_mpc"],
#         name="li_mpc",
#         texttemplate="%{x}",
#         textfont_size=20,
#     )
# )
#
# fig.show()

# %%
devel_df[SHOW_COLUMNS]
class_object.ion_concentration