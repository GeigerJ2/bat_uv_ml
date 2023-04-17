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
from project_data import *
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

# %% #? Convenience function to run the sampling for one structure and setup


def run_full_sampling(
    short_name,
    cell_size,
    ase_structure,
    group_label,
    relax_option,
):
    importlib.reload(pyconfsamp.core)

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
        clean_workdir=True,
    )

    # ? Submit Builders
    config_class.submit_builders(
        group_label=group_label,
    )
    # ? Create df which is linked to the class instance
    config_df = config_class.generate_df()
    # ? Save the df as a pickle file
    config_class.write_df(
        file_path="/home/jgeiger/projects/bat_uv_ml/data",
    )
    # ? Try pickling again
    config_class.pickle_me(
        file_path="/home/jgeiger/projects/bat_uv_ml/data",
    )

    return {"config_class": config_class, "config_df": config_df}


# %% #? Submit lfpo

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

# lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[0]
# lfpo_submission = run_full_sampling(
#     ase_structure=lfmpo_ase_structure,
#     short_name="lfmpo",
#     cell_size=1,
#     relax_option=1,
#     group_label="new_scf_hub/lfmpo-1/option1/fm",
# )

# %% #? Submit lfmpo

lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[1]
lfmpo_submission = run_full_sampling(
    ase_structure=lfmpo_ase_structure,
    short_name="lfmpo",
    cell_size=1,
    relax_option=1,
    group_label="new_scf_hub/lfmpo-1/option1/fm",
)

# %% #? Submit lmpo

lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[1]
# lfmpo_submission = run_full_sampling(
#     ase_structure=lfmpo_ase_structure,
#     short_name="lfmpo",
#     cell_size=1,
#     relax_option=1,
#     group_label="new_scf_hub/lfmpo-1/option1/fm",
# )

# %% # ? Run full stuff for LMPO
# importlib.reload(pyconfsamp.core)
#
# lmpo_config_class = pyconfsamp.core.ConfigClass()
# lmpo_sd = StructureData(ase=lmpo_ase)
#
# # lmpo_pmg_from_cathode = lmpo_cathode.as_ordered_structure()
# lmpo_config_class.short_name = "LMPO"
# lmpo_config_class.add_structuredata(lmpo_sd)
# lmpo_config_class.cell_size = 1
#
# # ? Prepare dictionary with specification of the configurations to be created
# # # ! Here was the error. Mn actually comes first, but index 0-4 was being treated as Li
# # # ! Another annoying issue is that .formula of pymatgen returns it sorted alphabetically it seems
# symbol_list = lmpo_ase.get_chemical_symbols()
# lmpo_config_dict = dict(
#     # substitution_sites=list(
#     #     range(symbol_list.index("Li"), len(symbol_list) - symbol_list[::-1].index("Li"))
#     # ),
#     cation_list=["Li", "Vac"],
#     concentration_restrictions={"Li": (0, 1)},
#     max_configurations=None,
#     symprec=GLOBAL_SYMPREC,
# )
#
# # ? Generate Configurations
# lmpo_config_class.generate_configs(config_dict=lmpo_config_dict)
# # ? Generate Hubbards
# lmpo_config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
# # ? Generate Builders
# lmpo_config_class.generate_builders(builder_dict=DEFAULT_BUILDER_DICT, relax_option=1)
# # ? Submit Builders
# lmpo_config_class.submit_builders(
#     group_label="new_scf_hub/lmpo-1/option1/fm",
#     parallelization="atoms",
#     clean_workdir=True,
# )
# # ? Create df which is linked to the class instance
# lmpo_config_df = lmpo_config_class.generate_df()
# # ? Save the df as a pickle file
# config_class.pickle_me(
#     file_path="/home/jgeiger/projects/bat_uv_ml/data",
#     file_name=group_label.replace("/", "-"),
# )


# %% #? Define convenience function for setting up sampling for one structure
