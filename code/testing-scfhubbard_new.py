# %%
import pathlib
from pprint import pprint

import numpy as np
import pandas as pd
from aiida import load_profile
from aiida.common import AttributeDict
from aiida.engine import submit
from aiida.orm import Bool, Dict, Int, Str, StructureData, load_node
from aiida.plugins import DataFactory
from aiida_quantumespresso.common.types import SpinType
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase.visualize import view
from own_utils.aiida.hp import generate_hubbards
from project_data import *
from project_functions import run_full_sampling
from qe_tools import CONSTANTS

# from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain

HubbardStructureData = DataFactory("quantumespresso.hubbard_structure")

load_profile()

# %% #? Create/read in HubbardStructureDatas

fully_lithiated_df = pd.read_pickle(
    "/home/jgeiger/projects/bat_uv_ml/data/fully_lithiated_df.pkl"
)
ase_list = fully_lithiated_df["ase_in"].values
centered_ase_list = []
for ase_structure in ase_list:
    ase_structure.center()
    centered_ase_list.append(ase_structure)

# view(centered_ase_list)

# sd_list = [StructureData(ase=_) for _ in centered_ase_list]

# hubbard_list = [
#     generate_hubbards(structuredata=_, hubbard_dict=DEFAULT_HUBBARD_DICT)
#     for _ in sd_list
# ]
# node_list = [_.store() for _ in hubbard_list]
# pk_list = [_.pk for _ in node_list]

pk_list = [58659, 58660, 58661, 58662, 58663]
name_list = ["lfpo", "lfmpo", "lmpo", "lmno", "lmo"]

# %% #? Try out lfpo with lower mixing beta and ion damping

for name, pk in list(zip(name_list, pk_list)):
    if name in ["lfpo", "lfmpo", "lmpo"]:
        option3_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
            pw_code=PW_CODE_LUMI,
            hp_code=HP_CODE_LUMI,
            hubbard_structure=load_node(pk),
            protocol="moderate",
            overrides=pathlib.Path(
                "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/lfpo_overrides.yaml"
            ),
            spin_type=SpinType.COLLINEAR,
        )

        # option3_builder.relax.base.pw.parameters["ELECTRONS"]["mixing_beta"] = 0.1
        # option3_builder.scf.pw.parameters["ELECTRONS"]["mixing_beta"] = 0.1

        # option3_builder.relax.base.pw.parameters["SYSTEM"] = AttributeDict(
        #     {"smearing": "gauss", "degauss": 0.05}
        # )
        # option3_builder.scf.pw.parameters["SYSTEM"] = AttributeDict(
        #     {"smearing": "gauss", "degauss": 0.05}
        # )

        # option3_builder.relax.base.pw.parameters["IONS"] = AttributeDict(
        #     {"trust_radius_min": 1e-4, "bfgs_ndim": 8}
        # )

        # option3_builder.relax.base.pw.parameters["IONS"] = AttributeDict(
        #     {"ion_dynamics": "damp"}
        # )

        # ? Defaults:  "conv_thr": 5.6e-09, "etot_conv_thr": 0.00028, "forc_conv_thr": 0.0001
        option3_builder.relax.base.pw.parameters["CONTROL"]["etot_conv_thr"] = 0.0028
        option3_builder.relax.base.pw.parameters["CONTROL"]["forc_conv_thr"] = 0.001
        option3_builder.relax.base.pw.parameters["ELECTRONS"]["conv_thr"] = 5.6e-8
        option3_builder.hubbard.hp.parameters["INPUTHP"]["dist_thr"] = 1e-1

        submit_node = submit(option3_builder)
        print(name, submit_node.pk)

# %% #? Try out new Lumi compilation

builder_lumi = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_LUMI,
    hp_code=HP_CODE_LUMI,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="fast",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/minimal_overrides.yaml"
    ),
)

submit_node_lumi = submit(builder_lumi)
print(submit_node_lumi)

# %% #? MN4

# Try new overrides
scf_hub_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_MN4,
    hp_code=HP_CODE_MN4,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="fast",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/minimal_overrides.yaml"
    ),
)

scf_hub_submit_node = submit(scf_hub_builder)
print(scf_hub_submit_node)

# %% #? Try out symlink

# Try new overrides
scf_hub_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_MN4,
    hp_code=HP_CODE_MN4,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="moderate",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/minimal_overrides.yaml"
    ),
)

scf_hub_submit_node = submit(scf_hub_builder)
print(scf_hub_submit_node)

# %% #? Try out relax frequency

scf_hub_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_MN4,
    hp_code=HP_CODE_MN4,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="moderate",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/minimal_overrides.yaml"
    ),
)

scf_hub_builder.relax_frequency = Int(3)

# %% #? Try out running on Eiger

builder_lumi = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_EIGER,
    hp_code=HP_CODE_EIGER,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="fast",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/minimal_overrides.yaml"
    ),
)

submit_node_lumi = submit(builder_lumi)
print(submit_node_lumi)

# %% #? See if parallelization option for hp is passed through

debug_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_EIGER,
    hp_code=HP_CODE_EIGER,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="moderate",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/debug_overrides.yaml"
    ),
)

debug_submit_node = submit(debug_builder)
print(debug_submit_node)

# %%

# print(debug_builder)
print(debug_builder.hubbard.hp.settings.get_dict())


# %% Full parallelization again

option3_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_EIGER,
    hp_code=HP_CODE_EIGER,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="fast",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/debug_overrides.yaml"
    ),
)

full_parallel_submit_node = submit(option3_builder)
print(full_parallel_submit_node)

# %%

# print(debug_builder)
print(option3_builder.hubbard.hp.settings.get_dict())


# %% #? Now with higher max_iterations in overrides, and with local-TF mixing, higher elecron_maxstep and higher nstep

for name, pk in list(zip(name_list, pk_list)):
    if name in ["lfpo", "lfmpo", "lmpo"]:
        option3_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
            pw_code=PW_CODE_LUMI,
            hp_code=HP_CODE_LUMI,
            hubbard_structure=load_node(pk),
            protocol="moderate",
            overrides=pathlib.Path(
                "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/lfpo_overrides.yaml"
            ),
        )

        submit_node = submit(option3_builder)
        print(name, submit_node.pk)

# %%
# ZERO_HUBBARD_DICT = {
#     "Mn": ("3d", 0.0001),
#     "Fe": ("3d", 0.0001),
#     "Ni": ("3d", 0.0001),
# }

# sd_list = [StructureData(ase=_) for _ in centered_ase_list]
# hubbard_list = [
#     generate_hubbards(structuredata=_, hubbard_dict=ZERO_HUBBARD_DICT) for _ in sd_list
# ]

# for ihubbard, hubbard in enumerate(hubbard_list):
#     option3_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
#         pw_code=PW_CODE_EIGER,
#         hp_code=HP_CODE_EIGER,
#         hubbard_structure=hubbard,
#         protocol="moderate",
#         overrides=pathlib.Path(
#             "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/lfpo_overrides.yaml"
#         ),
#     )

#     # option3_builder.skip_first_relax = False
#     # option3_builder.hubbard.parallelize_atoms = Bool(True)
#     # option3_builder.hubbard.parallelize_qpoints = Bool(False)
#     # option3_builder.hubbard.hp.settings.parent_folder_symlink = Bool(True)
#     # option3_builder.hubbard.max_iterations = Int(10)
#     # option3_builder.relax.base.max_iterations = Int(10)
#     # option3_builder.relax.max_meta_convergence_iterations = Int(10)
#     # option3_builder.scf.max_iterations = Int(10)
#     # option3_builder.max_iterations = Int(10)

#     submit_node = submit(option3_builder)
#     print(name_list[ihubbard], submit_node.pk)

# # %%
