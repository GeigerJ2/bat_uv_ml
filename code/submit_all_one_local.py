# %% # ? Imports
import os
from pathlib import Path

import pyconfsamp.core
from aiida import load_profile, orm
from aiida.orm import Group, load_code, load_group, load_node
from aiida_quantumespresso.common.types import SpinType
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
# %% # ? Loading stuff, structures, settings, etc.

# ? Where to move global variables ideally?
GLOBAL_SYMPREC = 1e-5
CELL_SIZE = 1
OPTION = 3

load_profile()

pw_code = orm.load_code("9145")
hp_code = orm.load_code("9146")

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
    "overrides": Path(os.path.join("yaml_files", "serial_overrides.yaml")),
    "spin_type": SpinType.COLLINEAR,
}

# %% # ? Initialize config_class

total_counter = 0
for short_name, structure_data in zip(fully_lithiated_names, structure_datas):
    config_class = pyconfsamp.core.ConfigClass()
    config_class.short_name = short_name
    config_class.add_structuredata(structure_data)
    config_class.cell_size = CELL_SIZE
    config_class.which_ones = "first"

    config_class.generate_configs(config_dict=CONFIG_DICT)
    config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    print(len(config_class.hubbard_configs))

    # config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    for option in [1, 2, 3]:
        # option_config_class = deepcopy(config_class)

        option_config_class.generate_builders(
            builder_dict=BUILDER_DICT, relax_option=OPTION
        )
        group_label = "testing/{}/{}".format(short_name, OPTION)
        # option_config_class.submit_builders(group_label=group_label)
        # total_counter += len(option_config_class.builders)
        # time.sleep(6 * 3600)
        print(group_label)

    # data_df = config_class.data_df()
    # print(data_df.shape)
    # data_df.head()

    #     break
    # break
print(total_counter)

# %%
