import os
from pathlib import Path

from aiida.orm import load_code
from aiida_quantumespresso.common.types import SpinType

PW_CODE_MN4 = load_code(24946)
HP_CODE_MN4 = load_code(24947)

# ? Where to move global variables ideally?
GLOBAL_SYMPREC = 1e-5

SORTING_DICT = {
    "Mn": 0,
    "Fe": 1,
    "Ni": 2,
    "O": 3,
    "P": 4,
    "Li": 5,
}

DEFAULT_BUILDER_DICT = {
    "pw_code": PW_CODE_MN4,
    "hp_code": HP_CODE_MN4,
    "protocol": "moderate",
    "overrides": Path(os.path.join("yaml_files", "minimal_overrides.yaml")),
    "spin_type": SpinType.COLLINEAR,
}

HUBBARD_DICT = {
    "Mn": ("3d", 5.5),  # ? Average between 4.6 and 6.6
    "Fe": ("3d", 5.3),
    "Ni": ("3d", 8.6),
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

# afm_relabel_dict = {
#     0: "Mn0",
#     1: "Mn0",
#     2: "Mn1",
#     3: "Mn1",
# }
#
# afm_mag_dict = {
#     "starting_magnetization": {
#         "Mn0": 0.5,
#         "Mn1": -0.5,
#         "O": 0.0,
#         "P": 0.0,
#         "Li": 0.0,
#     },
#     "nspin": 2,
# }
