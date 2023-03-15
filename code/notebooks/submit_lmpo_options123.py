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
from aiida import load_profile
from aiida.engine import submit
from aiida.orm import Bool, Group, Int, Str, load_code, load_group, load_node
from aiida_quantumespresso.common.types import SpinType
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase import Atoms
from ase.visualize import view
from pybat import Cathode
from pyconfsamp.core import change_atom_names
from pymatgen.io.ase import AseAtomsAdaptor

# from aiida.orm import UpfData, UpfFamily

# ? Where to move global variables ideally?
GLOBAL_SYMPREC = 1e-5

# %%
load_profile()
pw_code = load_code(2182)
hp_code = load_code(2183)

# %% [markdown]
# ### Read in fully lithiated structures

# %%

# ! Instead of using pandas df and pickle, directly store the node as StructureData in AiiDA
fully_lithiated_df = pd.read_pickle(
    os.path.join("..", "..", "data", "fully_lithiated_df.pkl")
)
print(fully_lithiated_df.shape)

# %%
# Setup of configuration sampling
lmpo_ase = fully_lithiated_df["ase_in"].values[2]
lmpo_ase.center()
sorting_dict = {
    "Mn": 0,
    "O": 1,
    "P": 2,
    "Li": 3,
}

# ! Does not take into account initial magmoms for now
lmpo_ase = Atoms(
    sorted(lmpo_ase, key=lambda x: sorting_dict[x.symbol]),
    cell=lmpo_ase.get_cell(),
    pbc=True,
)
lmpo_ase.center()
lmpo_ase.symbols
lmpo_pmg = AseAtomsAdaptor.get_structure(lmpo_ase)
lmpo_cathode = Cathode.from_structure(lmpo_pmg)

import pyconfsamp.core
from pybat.core import Cathode

# %%
from pymatgen.core import Structure

importlib.reload(pyconfsamp.core)
lmpo_config_class = pyconfsamp.core.ConfigClass()

symbol_list = lmpo_ase.get_chemical_symbols()
lmpo_pmg_from_cathode = lmpo_cathode.as_ordered_structure()
lmpo_config_class.short_name = "LMPO"
lmpo_config_class.add_cathode(lmpo_cathode)
lmpo_config_class.eval_parent_sg()
lmpo_config_class.cell_size = 1

# Run configuration sampling
# ! Here was the error. Mn actually comes first, but index 0-4 was being treated as Li
# ! Another annoying issue is that .formula of pymatgen returns it sorted alphabetically it seems
lmpo_config_dict = dict(
    substitution_sites=list(
        range(symbol_list.index("Li"), len(symbol_list) - symbol_list[::-1].index("Li"))
    ),
    cation_list=["Li", "Vac"],
    concentration_restrictions={"Li": (0, 1)},
    max_configurations=None,
    symprec=GLOBAL_SYMPREC,
)
lmpo_config_class.create_configurations(**lmpo_config_dict)

# Create df which is linked to the class instance
lmpo_config_class.attach_df()

lmpo_config_df = lmpo_config_class.data_df

# %%
relabel_dict = {
    0: "Mn1",
    1: "Mn1",
    2: "Mn2",
    3: "Mn2",
}

afm_mag_dict = {
    "starting_magnetization": {
        "Mn1": 0.5,
        "Mn2": -0.5,
        "O": 0.0,
        "P": 0.0,
        "Li": 0.0,
    },
    "nspin": 2,
}

default_builder_dict = {
    "pw_code": pw_code,
    "hp_code": hp_code,
    "protocol": "moderate",
    "overrides": Path(
        os.path.join("..", "yaml_files", "basically_empty_overrides.yaml")
    ),
}
#%%

# ! Submission of LMPO-1 configurations with option 1
submission_group_label = "testing/lmpo-1/option1"
# submission_group = Group(submission_group_label)
# submission_group.store()
submission_group = load_group(submission_group_label)

for itertuple in list(lmpo_config_df.itertuples())[-1:]:

    # print(type(itertuple))
    # print(itertuple)
    structuredata = itertuple.structuredata
    formula = structuredata.get_formula(mode="reduce")
    print(formula)

    # ? Differentiate different Mn sites
    structuredata = change_atom_names(
        structure_data=structuredata, relabel_dict=relabel_dict
    )

    # ? Create HubbardStructure from StructureData with initialized U/V
    hubbard_structure = HubbardStructureData(structure=structuredata)
    hubbard_structure.initialize_onsites_hubbard("Mn1", "3d", 4.5618)
    hubbard_structure.initialize_onsites_hubbard("Mn2", "3d", 4.5618)
    hubbard_structure.initialize_intersites_hubbard(
        "Mn1", "3d", "O", "2p", 0.0001, number_of_neighbours=7
    )
    hubbard_structure.initialize_intersites_hubbard(
        "Mn2", "3d", "O", "2p", 0.0001, number_of_neighbours=7
    )

    # ? Populate builder
    builder_dict = default_builder_dict.copy()
    builder_dict["hubbard_structure"] = hubbard_structure
    builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(**builder_dict)

    # ? Modify builder, in this case for SS
    _ = builder.pop("relax", None)
    builder.meta_convergence = Bool(False)
    builder.max_iterations = Int(1)
    if "Li" in formula:
        builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict
    else:
        noli_mag_dict = afm_mag_dict.copy()
        noli_mag_dict["starting_magnetization"].pop("Li")
        builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict

    # print(builder)
    scf_dict = builder.scf.pw.parameters.get_dict()
    hubbard_dict = builder.hubbard.hp.parameters.get_dict()

    # print(json.dumps(scf_dict, sort_keys=False, indent=4))
    # print(json.dumps(relax_dict, sort_keys=False, indent=4))
    # print(json.dumps(hubbard_dict, sort_keys=False, indent=4))

    lmpo_1_ss_submit = submit(builder)
    submission_group.add_nodes(lmpo_1_ss_submit)

#%%
# ! Submission of LMPO-1 configurations with option 2
submission_group_label = "testing/lmpo-1/option2"
# submission_group = Group(submission_group_label)
# submission_group.store()
submission_group = load_group(submission_group_label)

for itertuple in list(lmpo_config_df.itertuples()):

    # print(type(itertuple))
    # print(itertuple)
    structuredata = itertuple.structuredata
    formula = structuredata.get_formula(mode="reduce")
    print(formula)

    # ? Differentiate different Mn sites
    structuredata = change_atom_names(
        structure_data=structuredata, relabel_dict=relabel_dict
    )

    # ! All of this duplicated right now. Store structuredata and hubbard_structure in df or class instance.
    # ? Create HubbardStructure from StructureData with initialized U/V
    hubbard_structure = HubbardStructureData(structure=structuredata)
    hubbard_structure.initialize_onsites_hubbard("Mn1", "3d", 4.5618)
    hubbard_structure.initialize_onsites_hubbard("Mn2", "3d", 4.5618)
    hubbard_structure.initialize_intersites_hubbard(
        "Mn1", "3d", "O", "2p", 0.0001, number_of_neighbours=7
    )
    hubbard_structure.initialize_intersites_hubbard(
        "Mn2", "3d", "O", "2p", 0.0001, number_of_neighbours=7
    )

    # ? Populate builder
    builder_dict = default_builder_dict.copy()
    builder_dict["hubbard_structure"] = hubbard_structure
    option2_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
        **builder_dict
    )

    # ? Modify builder, in this case for SS
    _ = option2_builder.pop("relax", None)
    # builder.meta_convergence = Bool(False)
    # builder.max_iterations = Int(1)
    if "Li" in formula:
        option2_builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict
    else:
        noli_mag_dict = deepcopy(afm_mag_dict)
        _ = noli_mag_dict["starting_magnetization"].pop("Li")
        option2_builder.scf.pw.parameters["SYSTEM"] = noli_mag_dict

    lmpo_2_ss_submit = submit(option2_builder)
    submission_group.add_nodes(lmpo_2_ss_submit)

#%%

# ! Submission of LMPO-1 configurations with option 3
submission_group_label = "testing/lmpo-1/option3"
try:
    submission_group = Group(submission_group_label)
    submission_group.store()
except:
    submission_group = load_group(submission_group_label)

for itertuple in list(lmpo_config_df.itertuples()):

    # print(type(itertuple))
    # print(itertuple)
    structuredata = itertuple.structuredata
    formula = structuredata.get_formula(mode="reduce")
    print(formula)

    # ? Differentiate different Mn sites
    structuredata = change_atom_names(
        structure_data=structuredata, relabel_dict=relabel_dict
    )

    # ! All of this duplicated right now. Store structuredata and hubbard_structure in df or class instance.
    # ? Create HubbardStructure from StructureData with initialized U/V
    hubbard_structure = HubbardStructureData(structure=structuredata)
    hubbard_structure.initialize_onsites_hubbard("Mn1", "3d", 4.5618)
    hubbard_structure.initialize_onsites_hubbard("Mn2", "3d", 4.5618)
    hubbard_structure.initialize_intersites_hubbard(
        "Mn1", "3d", "O", "2p", 0.0001, number_of_neighbours=7
    )
    hubbard_structure.initialize_intersites_hubbard(
        "Mn2", "3d", "O", "2p", 0.0001, number_of_neighbours=7
    )

    # ? Populate builder
    builder_dict = default_builder_dict.copy()
    builder_dict["hubbard_structure"] = hubbard_structure
    option3_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
        **builder_dict
    )

    # ? Modify builder, in this case for SS
    # _ = option3_builder.pop("relax", None)
    # builder.meta_convergence = Bool(False)
    # builder.max_iterations = Int(1)
    if "Li" in formula:
        option3_builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict
    else:
        noli_mag_dict = deepcopy(afm_mag_dict)
        _ = noli_mag_dict["starting_magnetization"].pop("Li")
        option3_builder.scf.pw.parameters["SYSTEM"] = noli_mag_dict

    lmpo_3_submit = submit(option3_builder)
    submission_group.add_nodes(lmpo_3_submit)
