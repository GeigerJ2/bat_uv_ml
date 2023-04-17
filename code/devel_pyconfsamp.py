# %% # ? Imports
import importlib
import os
from pathlib import Path

import ase
import pandas as pd
import pyconfsamp.core
from aiida import load_profile
from aiida.orm import Group, load_code, load_group, load_node
from aiida_quantumespresso.common.types import SpinType
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

pd.set_option("display.max_rows", None)
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

# CONFIG_DICT = {
#     "cation_list": ["Li", "Vac"],
#     "concentration_restrictions": {"Li": (0, 1)},
#     "max_configurations": None,
#     "symprec": GLOBAL_SYMPREC,
# }

HUBBARD_DICT = {
    "Mn": ("3d", 5.5),  # ? Average between 4.6 and 6.6
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
    "li_conc",
    # "cell_index",
    "conc_index",
    "li_mpc",
    "cell_mpc",
    "sg_mpc",
    "specific_name",
]

# %% # ? Development for cell size of 2

importlib.reload(pyconfsamp.core)

for short_name, structure_data in zip(fully_lithiated_names, structure_datas):
    # print(short_name)
    # break
    if short_name == "LMPO":
        config_class = pyconfsamp.core.ConfigClass()
        config_class.short_name = short_name
        config_class.add_structuredata(structure_data)
        config_class.cell_size = 1

        config_class.generate_configs(config_dict=CONFIG_DICT)
        group_label = "testing/{}/{}/{}".format(short_name, 2, OPTION)
        print(group_label)
        config_class.pickle_me(
            file_path="/home/jgeiger/projects/bat_uv_ml/data",
            file_name=group_label.replace("/", "_"),
        )
        # config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
        # config_class.generate_builders(builder_dict=BUILDER_DICT, relax_option=OPTION)
        # config_class.submit_builders(group_label=group_label)

        data_df = config_class.data_df()
        data_df[SHOW_COLUMNS].head(11).to_csv(
            "/home/jgeiger/projects/bat_uv_ml/data/{}.csv".format(
                group_label.replace("/", "_")
            )
        )
        data_df[SHOW_COLUMNS].head(10)

# %%


data_df.columns

sorted_data_df = data_df.sort_values(by=["cell_vectors", "li_conc"])
# view(sorted_data_df["ase_structure"])
atoms_list = sorted_data_df["ase_structure"].tolist()

# atoms_list = [_.center()for _ in atoms_list]
ase.io.write(
    filename="/home/jgeiger/projects/bat_uv_ml/data/lmpo_movie.xyz",
    images=atoms_list,
    format="extxyz",
)


# %%
view(data_df["ase_structure"])

# %% # ? Generate all the configs

importlib.reload(pyconfsamp.core)

for short_name, structure_data in zip(fully_lithiated_names, structure_datas):
    if short_name in fully_lithiated_names[:3]:
        print(short_name)
        cell_sizes = [1, 2]
    else:
        cell_sizes = [1]
    for cell_size in cell_sizes:
        config_class = pyconfsamp.core.ConfigClass()
        config_class.short_name = short_name
        config_class.add_structuredata(structure_data)
        config_class.cell_size = cell_size

        config_class.generate_configs(config_dict=CONFIG_DICT)
        group_label = "testing/{}/{}/{}".format(short_name, cell_size, OPTION)
        config_class.pickle_me(
            file_path="/home/jgeiger/projects/bat_uv_ml/data",
            file_name=group_label.replace("/", "_"),
        )
        # config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
        # config_class.generate_builders(builder_dict=BUILDER_DICT, relax_option=OPTION)
        # config_class.submit_builders(group_label=group_label)

        data_df = config_class.data_df()
        # data_df.to_pickle(
        #             data_df.to_pickle()
        print(group_label, data_df.shape)

    # break


# %%

# df_dict = {}

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
# %%

devel_df = df_dict["testing_LMPO_2_3"]
devel_df[SHOW_COLUMNS].sort_values(by=["li_conc"])
