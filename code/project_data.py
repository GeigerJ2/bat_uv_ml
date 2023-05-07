import os
from pathlib import Path

from aiida import load_profile
from aiida.orm import load_code, load_node
from aiida_quantumespresso.common.types import SpinType

load_profile()

PROJECT_DIR = "/home/jgeiger/projects/bat_uv_ml/code"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
CODE_DIR = os.path.join(PROJECT_DIR, "code")
FIGS_DIR = os.path.join(PROJECT_DIR, "figs")

PW_CODE_MN4 = load_code(24946)
HP_CODE_MN4 = load_code(24947)
PW_CODE_LUMI = load_code(70053)
HP_CODE_LUMI = load_code(70054)
# PW_CODE_LUMI = load_code(2182)
# HP_CODE_LUMI = load_code(2183)
PW_CODE_LOCAL = load_code(34982)
HP_CODE_LOCAL = load_code(34983)
PW_CODE_EIGER = load_code(44762)
HP_CODE_EIGER = load_code(44763)

BATIO3_HUBBARD_DATA = load_node(19376)

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
    "pw_code": PW_CODE_LUMI,
    "hp_code": HP_CODE_LUMI,
    "protocol": "moderate",
    "overrides": Path(os.path.join("yaml_files", "low_thresh_overrides.yaml")),
    "spin_type": SpinType.COLLINEAR,
}

DEFAULT_HUBBARD_DICT = {
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
