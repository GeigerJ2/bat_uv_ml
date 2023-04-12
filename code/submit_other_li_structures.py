# %% # ? Imports
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import os
from pathlib import Path

import pandas as pd
import pyconfsamp.core
from aiida import load_profile
from aiida.engine import submit
from aiida.orm import (Bool, Group, Int, Str, StructureData, load_code,
                       load_group, load_node)
from aiida.orm.nodes.data.array.kpoints import KpointsData
from aiida_quantumespresso.common.types import SpinType
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida_quantumespresso.workflows.pw.base import PwBaseWorkChain
from aiida_quantumespresso_hp.workflows.hubbard import \
    SelfConsistentHubbardWorkChain
from ase import Atoms
from ase.visualize import view
from pybat import Cathode
from pybat.core import Cathode
from pyconfsamp.core import change_atom_names
from pymatgen.io.ase import AseAtomsAdaptor
from sqlalchemy.exc import IntegrityError

# from aiida.orm import UpfData, UpfFamily

# ? Where to move global variables ideally?
GLOBAL_SYMPREC = 1e-5

# %% # ? Load AiiDA stuff, structures, etc.
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

# %% # ? Former loading of structures from df

# ! Instead of using pandas df and pickle, directly store the node as StructureData in AiiDA
# fully_lithiated_df = pd.read_pickle(
#     os.path.join("..", "data", "fully_lithiated_df.pkl")
# )
# %% # ? Sort Atoms and store structuredatas

# sorting_dict = {
#     "Mn": 0,
#     "Fe": 1,
#     "Ni": 2,
#     "O": 3,
#     "P": 4,
#     "Li": 5,
# }

# ase_structures = fully_lithiated_df["ase_in"].values

# # ! Does not take into account initial magmoms for now
# ase_structures = [
#     Atoms(
#         sorted(ase_structure, key=lambda x: sorting_dict[x.symbol]),
#         cell=ase_structure.get_cell(),
#         pbc=True,
#     )
#     for ase_structure in ase_structures
# ]

# # sorted_ase_structure = ase_structure.center() for ase_structure in sorted_ase_structures]
# print([_.symbols for _ in ase_structures])
# _ = [ase_structure.center() for ase_structure in ase_structures]
# pmg_structures = [
#     AseAtomsAdaptor.get_structure(ase_structure) for ase_structure in ase_structures
# ]

# structure_datas = [
#     StructureData(pymatgen_structure=pmg_structure) for pmg_structure in pmg_structures
# _ = [structure_data.store() for structure_data in structure_datas]
# print([structure_data.pk for structure_data in structure_datas])
# cathode_structures = [
#     Cathode.from_structure(pmg_structure) for pmg_structure in pmg_structures
# ]

# %% # ? Former AFM magnetization setting for LMPO configurations

# relabel_dict = {
#     0: "Mn0",
#     1: "Mn0",
#     2: "Mn1",
#     3: "Mn1",
# }

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

# structuredata = change_atom_names(
#     structure_data=structuredata, relabel_dict=relabel_dict
# )

# if "Li" in formula:
#     builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict
# else:
#     noli_mag_dict = deepcopy(afm_mag_dict)
#     noli_mag_dict["starting_magnetization"].pop("Li")
#     builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict


# %% # ? Group loading
submission_group_label = "testing/lithiated_structures/option3/nomag"
try:
    submission_group = Group(submission_group_label)
    submission_group.store()
except:  # IntegrityError:
    submission_group = load_group(submission_group_label)

# %% # ? Initialize Hubbard


def prepare_builder(
    structuredata: StructureData,
    hubbard_dict: dict,
    builder_dict: None,
    hubbard_atoms: list = None,
    mag_dict: dict = None,  # ? This here, or internally as default?
    option: int = 3,
    num_neighbors: int = 7,
):
    """Convenience function to prepare builder for olivine and spinel
    submission, including magnetic ordering and Hubbard parameters.

    Args:
        structuredata (StructureData): Structuredata instance.
        hubbard_atoms (List): Currently only first Hubbard atom, as neighbor is always oxygen.
        hubbard_dict (dict): Dictionary with hubbard element, manifold, and starting value.
        mag_dict (dict, optional): Dictionary with magnetizations. Defaults to None.
        option (int, optional): "Options", that is SS, fixed positions, or fully SC. Defaults to 3.
        num_neighbors (int, optional): Number of neighbors + 1. Defaults to 7.
    """
    if hubbard_atoms is None:
        hubbard_atoms = [
            atom
            for atom in ["Mn", "Fe", "Ni"]
            if atom in structuredata.get_formula(mode="reduce")
        ]

    hubbard_structure = HubbardStructureData(structure=structuredata)
    for hubbard_atom in hubbard_atoms:
        hubbard_structure.initialize_onsites_hubbard(
            hubbard_atom, *hubbard_dict[hubbard_atom]
        )
        hubbard_structure.initialize_intersites_hubbard(
            atom_name=hubbard_atom,
            atom_manifold=hubbard_dict[hubbard_atom][0],
            neighbours_name="O",
            neighbours_manifold="2p",
            value=0.0001,
            number_of_neighbours=num_neighbors,
        )

    # builder_dict_ = deepcopy(builder_dict)
    builder_dict_["hubbard_structure"] = hubbard_structure
    builder_ = SelfConsistentHubbardWorkChain.get_builder_from_protocol(**builder_dict_)

    # Set qpoints "manually"
    qpoints = KpointsData()
    qpoints.set_cell_from_structure(structuredata=hubbard_structure)
    qpoints.set_kpoints_mesh_from_density(distance=1.2)
    builder_.hubbard.hp.qpoints = qpoints

    # Set calculation spinpolarized
    # builder_.scf.pw.parameters["SYSTEM"] = {"nspin": 2}

    # Different options of running the calculation
    if option != 3:
        _ = builder_.pop("relax", None)
        if option == 1:
            builder_.meta_convergence = Bool(False)
            builder_.max_iterations = Int(1)

    # Add magnetic ordering in the future
    _ = mag_dict
    print(hubbard_structure.get_quantum_espresso_hubbard_card())
    # print(builder_.scf.pw.parameters.get_dict())
    # print(builder_.relax.base)
    # print(builder_.hubbard.hp)
    # scf_dict = builder.scf.pw.parameters.get_dict()
    # hubbard_dict = builder.hubbard.hp.parameters.get_dict()
    return builder_


# %% # ? Actually running builder function and submitting

default_hubbard_dict = {
    "Mn": ("3d", 5.6),  # ? Average between 4.6 and 6.6
    "Fe": ("3d", 5.3),
    "Ni": ("3d", 8.6),
}

default_builder_dict = {
    "pw_code": pw_code,
    "hp_code": hp_code,
    "protocol": "moderate",
    "overrides": Path(os.path.join("yaml_files", "default_overrides.yaml")),
    "spin_type": SpinType.COLLINEAR,
}

# pattern = r"\b({})\b".format("|".join(map(test_string, hubbard_atoms)))
fully_lithiated_builders = []
for structure_data in structure_datas:
    print(structure_data.get_formula(mode="reduce"))
    builder = prepare_builder(
        structuredata=structure_data,
        option=3,
        hubbard_dict=default_hubbard_dict,
        builder_dict=default_builder_dict,
    )
    fully_lithiated_builders.append(builder)

    # builder_submit = submit(builder)
    # submission_group.add_nodes(builder_submit)


# %% # ? Builder

# default_builder_dict = {
#     "pw_code": pw_code,
#     "hp_code": hp_code,
#     "protocol": "moderate",
#     "overrides": Path(os.path.join("..", "yaml_files", "default_overrides.yaml")),
# }

# builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
#     pw_code=pw_code,
#     hp_code=hp_code,
#     protocol="moderate",
#     overrides=Path(os.path.join("..", "yaml_files", "default_overrides.yaml")),
#     hubbard_structure=devel_hubbard_structure,
# )

# qpoints = KpointsData()
# qpoints.set_cell_from_structure(structuredata=devel_hubbard_structure)
# qpoints.set_kpoints_mesh_from_density(distance=1.2)

# builder.hubbard.hp.qpoints = qpoints
# devel_hubbard_structure.cell

# print(builder.hubbard.hp.qpoints.get_kpoints_mesh())

# ! option1
# _ = builder.pop("relax", None)
# builder.meta_convergence = Bool(False)
# builder.max_iterations = Int(1)
# ! option2
# _ = option2_builder.pop("relax", None)
# ! option3

# %% # ? Former submission for group1

# for itertuple in list(lmpo_config_df.itertuples())[-2:]:

# structuredata = itertuple.structuredata
# formula = structuredata.get_formula(mode="reduce")
# print(formula)

# # ? Differentiate different Mn sites

# # ? Create HubbardStructure from StructureData with initialized U/V

# # ? Populate builder
# builder_dict = default_builder_dict.copy()
# builder_dict["hubbard_structure"] = hubbard_structure
# builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(**builder_dict)

# # ? Modify builder, in this case for SS

# scf_dict = builder.scf.pw.parameters.get_dict()
# hubbard_dict = builder.hubbard.hp.parameters.get_dict()

# lmpo_1_ss_submit = submit(builder)
# submission_group.add_nodes(lmpo_1_ss_submit)


# custom_slice = itemgetter(2, 3, 5, 6)
# submission_group_label = "testing/lmpo-1/option2"
# submission_group = load_group(submission_group_label)

# for itertuple in list(lmpo_config_df.itertuples()):

#     structuredata = itertuple.structuredata
#     formula = structuredata.get_formula(mode="reduce")
#     print(itertuple.Index, formula)
#     if itertuple.Index in [2, 3, 5, 6]:

#         # ? Differentiate different Mn sites
#         structuredata = change_atom_names(
#             structure_data=structuredata, relabel_dict=relabel_dict
#         )

#         # ! All of this duplicated right now. Store structuredata and hubbard_structure in df or class instance.
#         # ? Create HubbardStructure from StructureData with initialized U/V
#         hubbard_structure = HubbardStructureData(structure=structuredata)
#         hubbard_structure.initialize_onsites_hubbard("Mn1", "3d", 4.5)
#         hubbard_structure.initialize_onsites_hubbard("Mn2", "3d", 4.6)
#         hubbard_structure.initialize_intersites_hubbard(
#             "Mn1", "3d", "O", "2p", 0.0001, number_of_neighbours=7
#         )
#         hubbard_structure.initialize_intersites_hubbard(
#             "Mn2", "3d", "O", "2p", 0.0001, number_of_neighbours=7
#         )

#         # ? Populate builder
#         builder_dict = default_builder_dict.copy()
#         builder_dict["hubbard_structure"] = hubbard_structure
#         option2_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
#             **builder_dict
#         )

#         # ? Modify builder, in this case for SS
#         _ = option2_builder.pop("relax", None)

#         if "Li" in formula:
#             option2_builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict
#         else:
#             noli_mag_dict = deepcopy(afm_mag_dict)
#             _ = noli_mag_dict["starting_magnetization"].pop("Li")
#             option2_builder.scf.pw.parameters["SYSTEM"] = noli_mag_dict

#         lmpo_2_ss_submit = submit(option2_builder)
#         submission_group.add_nodes(lmpo_2_ss_submit)

# %%
print("test")
