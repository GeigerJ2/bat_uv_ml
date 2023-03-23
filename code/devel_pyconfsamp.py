# %% # ? Imports
import importlib
import os
from pathlib import Path

import pyconfsamp.core
from aiida import load_profile
from aiida.orm import Group, load_code, load_group, load_node
from aiida_quantumespresso.common.types import SpinType
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
#%% # ? Loading stuff, structures, settings, etc.

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

#%% # ? Initialize config_class

importlib.reload(pyconfsamp.core)

for short_name, structure_data in zip(fully_lithiated_names, structure_datas):

    config_class = pyconfsamp.core.ConfigClass()
    config_class.short_name = short_name
    config_class.add_structuredata(structure_data)
    config_class.cell_size = CELL_SIZE

    config_class.generate_configs(config_dict=CONFIG_DICT)
    # config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    # config_class.generate_builders(builder_dict=BUILDER_DICT, relax_option=OPTION)
    group_label = "testing/{}/{}".format(short_name, OPTION)
    # config_class.submit_builders(group_label=group_label)
    config_class.pickle_me(
        file_path="/home/jgeiger/projects/bat_uv_ml/data",
        file_name=group_label.replace("/", "_"),
    )

    data_df = config_class.data_df()
    # data_df.head()

    break

#%% # ? Develop changing the magnetization

_ = importlib.reload(pyconfsamp.core)

RELABEL_DICT = {
    0: "Mn0",
    1: "Mn0",
    2: "Mn1",
    3: "Mn1",
}

MAG_DICT = {
    "Mn0": 0.5,
    "Mn1": -0.5,
    # ? The following ones could be set via dict.get(default: 0.0)
    "O": 0.0,
    "P": 0.0,
    "Li": 0.0,
    # "nspin": 2,
}

for short_name, structure_data in list(zip(fully_lithiated_names, structure_datas))[
    2:3
]:

    config_class = pyconfsamp.core.ConfigClass()
    config_class.short_name = short_name
    magnetic_structure_data = structure_data.clone()
    # print(magnetic_structure_data.get_formula(mode="reduce"))
    # print(magnetic_structure_data.get_ase().get_chemical_symbols())
    # ! Now the relabelling needs to be done outside, as ASE and pymatgen internally don't like custom labels.
    magnetic_structure_data = pyconfsamp.core.change_atom_names(
        structure_data=magnetic_structure_data, relabel_dict=RELABEL_DICT
    )
    # print(magnetic_structure_data.get_formula(mode="reduce"))

    config_class.add_structuredata(structuredata=structure_data)
    config_class.cell_size = CELL_SIZE
    config_class.which_ones = "first"

    config_class.generate_configs(config_dict=CONFIG_DICT)
    config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    config_class.generate_builders(
        builder_dict=BUILDER_DICT, relax_option=OPTION, mag_dict=MAG_DICT
    )

    group_label = "testing/{}/{}".format(short_name, OPTION)
    print(group_label)
    config_class.submit_builders(group_label=group_label)

    # data_df = config_class.data_df()
    # # data_df.head()
    # data_df["pmg_structure"].values[0]

    break

#%%

config_class.generate_df()

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
# hubbard_dict = {
#     "olivine": {"Mn": ("3d", 4.6), "Fe": ("3d", 5.3)},
#     "spinel": {"Mn": ("3d", 6.6), "Ni": ("3d", 8.6)},
# }

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

#%%
print("test")
