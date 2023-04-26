# %%
import pathlib

import numpy as np
from aiida import load_profile, orm
from aiida.engine import submit
from aiida.orm import Int
from aiida.plugins import DataFactory
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from project_data import *
from qe_tools import CONSTANTS

# load_profile()

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

builder_eiger = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_EIGER,
    hp_code=HP_CODE_EIGER,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="fast",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/minimal_overrides.yaml"
    ),
)

eiger_submit_node = submit(builder_eiger)
print(eiger_submit_node)

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

full_parallel_builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
    pw_code=PW_CODE_EIGER,
    hp_code=HP_CODE_EIGER,
    hubbard_structure=BATIO3_HUBBARD_DATA,
    protocol="fast",
    overrides=pathlib.Path(
        "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/debug_overrides.yaml"
    ),
)

full_parallel_submit_node = submit(full_parallel_builder)
print(full_parallel_submit_node)

# %%

# print(debug_builder)
print(full_parallel_builder.hubbard.hp.settings.get_dict())
