# %%
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import importlib
import json
import os
from copy import deepcopy
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

# pd.set_option('display.max_colwidth', None)
# fully_li_columns = [
#     "calc_in",
#     "calc_name",
#     "calc_type",
#     "calc_out",
#     "clean_input_file",
#     "chem_formula",
#     "chem_symbols",
# ]
# fully_lithiated_df[fully_li_columns].head(5)  # ! LPPO, then mixed, then LMPO, then spinels
# all_ase_structures = fully_lithiated_df["ase_in"].values
# view(all_ase_structures)


# %% #? Convenience function to run the sampling for one structure and setup

importlib.reload(pyconfsamp.core)


def run_full_sampling(
    short_name,
    cell_size,
    ase_structure,
    group_label,
    relax_option,
    submit_index: int = None,
):
    config_class = pyconfsamp.core.ConfigClass()
    # ! Does not take into account initial magmoms for now
    ase_structure = Atoms(
        sorted(ase_structure, key=lambda x: SORTING_DICT[x.symbol]),
        cell=ase_structure.get_cell(),
        pbc=True,
    )
    ase_structure.center()
    structuredata = StructureData(ase=ase_structure)

    config_class.short_name = short_name
    config_class.add_structuredata(structuredata)
    config_class.cell_size = cell_size

    config_dict = dict(
        cation_list=["Li", "Vac"],
        concentration_restrictions={"Li": (0, 1)},
        max_configurations=None,
        symprec=GLOBAL_SYMPREC,
    )

    # ? Generate Configurations
    config_class.generate_configs(config_dict=config_dict)
    # ? Generate Hubbards
    config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    # ? Generate Builders
    config_class.generate_builders(
        builder_dict=DEFAULT_BUILDER_DICT,
        relax_option=relax_option,
        parallelization="atoms",
        clean_workdir=False,
    )

    # ? Submit Builders
    config_class.submit_builders(
        group_label=group_label,
        submit_index=submit_index,
    )
    # ? Create df which is linked to the class instance
    config_df = config_class.generate_df()
    # ? Save the df as a pickle file
    # config_class.write_df(
    #     file_path="/home/jgeiger/projects/bat_uv_ml/data",
    # )
    # # # ? Try pickling again
    # config_class.pickle_me(
    #     file_path="/home/jgeiger/projects/bat_uv_ml/data",
    # )

    return {"config_class": config_class, "config_df": config_df}


# %% #? Submit lmpo at option 1

lmpo_submission = run_full_sampling(
    ase_structure=lmpo_ase_structure,
    short_name="lmpo",
    cell_size=1,
    relax_option=1,
    group_label="eiger_test/lmpo-1/option1/fm",
    submit_index=0,
)

# %% #? Submit lmpo at option 2

lmpo_submission = run_full_sampling(
    ase_structure=lmpo_ase_structure,
    short_name="lmpo",
    cell_size=1,
    relax_option=2,
    group_label="eiger_test/lmpo-1/option2/fm",
    submit_index=0,
)

# %% #? Submit lmpo at option 3

lmpo_submission = run_full_sampling(
    ase_structure=lmpo_ase_structure,
    short_name="lmpo",
    cell_size=1,
    relax_option=3,
    group_label="eiger_test/lmpo-1/option3/fm",
    submit_index=0,
)
# %% #? Submit lfpo

lfpo_submission = run_full_sampling(
    ase_structure=lfpo_ase_structure,
    short_name="lfpo",
    cell_size=1,
    relax_option=1,
    group_label="eiger_test/lfpo-1/option1/fm",
    submit_index=0,
)

# %% #? Submit lfmpo

lfmpo_submission = run_full_sampling(
    ase_structure=lfmpo_ase_structure,
    short_name="lfmpo",
    cell_size=1,
    relax_option=1,
    group_label="eiger_test/lfmpo-1/option1/fm",
    submit_index=0,
)
