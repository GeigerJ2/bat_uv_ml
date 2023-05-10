# %%
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
import os
from pathlib import Path
from pprint import pprint

import pandas as pd
from aiida import load_profile
from aiida.orm import load_node
from ase import Atoms
from ase.visualize import view
from project_data import DEFAULT_BUILDER_DICT
from project_functions import run_full_sampling

# from aiida.orm import UpfData, UpfFamily

load_profile()


# %% #? Read in df of fully lithiated structures

# ! Instead of using pandas df and pickle, directly store the node as StructureData in AiiDA
# fully_lithiated_df = pd.read_pickle(
#     os.path.join("..", "data", "fully_lithiated_df.pkl")
# )
# print(fully_lithiated_df.shape)
# fully_lithiated_df.head()

# lfpo_ase_structure = fully_lithiated_df["ase_in"].values[0]
# lfmpo_ase_structure = fully_lithiated_df["ase_in"].values[1]
# lmpo_ase_structure = fully_lithiated_df["ase_in"].values[2]


# %% #? Submit lfmpo with the hopefully working settings.

builder_dict = dict(DEFAULT_BUILDER_DICT)
builder_dict["overrides"] = Path(
    os.path.join("yaml_files", "low_thresh_overrides.yaml")
)

pk_list = [58659, 58660, 58661, 58662, 58663]
name_list = ["lfpo", "lfmpo", "lmpo", "lmno", "lmo"]

for name, pk in list(zip(name_list, pk_list)):
    if name in ["lfpo", "lfmpo", "lmpo"]:
        for option in [3]:
            lfmpo_submission = run_full_sampling(
                ase_structure=load_node(pk).get_ase(),
                short_name=name,
                cell_size=1,
                relax_option=option,
                group_label="lower_thresh/{}-1/option{}/fm".format(name, option),
                builder_dict=builder_dict,
                submit_index=5,
            )
    #         break
    # break

# %%

node = load_node(83284)
node.base.repository.list_object_names()
print(node.outputs.retrieved)

node.base.repository.get_object_content()

# %%

hubbard_node_initial = load_node(58659)
hubbard_class_initial = hubbard_node_initial.hubbard

# pprint(type(hubbard_node_initial.hubbard))
print(hubbard_node_initial.sites)
pprint(hubbard_node_initial.hubbard.to_list())

hubbard_node_submit = load_node(80687)
hubbard_class_final = hubbard_node_submit.hubbard
view([hubbard_node_initial.get_ase(), hubbard_node_submit.get_ase()])


# %%
# Copied here from the pointless pyconfsamp class.
def symmetry_inequiv(ase_in):
    return


def initialize_hubbard(
    ase_structure: Atoms,
    hubbard_dict: dict,
    hubbard_atoms: list = None,
):
    """Generate HubbardStructureData objects.

    Args:
        hubbard_dict (dict): Dictionary containing atoms as keys and (manifold, U) as values.
        num_neighbors (int, optional): Number of neighbors (+1). Defaults to 7.
        hubbard_atoms (list, optional): List of Hubbard Atoms. Defaults to None.
    """
    if hubbard_atoms is None:
        hubbard_atoms = [
            atom for atom in ["Mn", "Fe", "Ni"] if atom in ase_structure.symbols
        ]

    # ? It should be OK, as I'm passing the full ase_structure to HubbardStructureData.
    hubbard_structure = HubbardStructureData.from_structure(structure=ase_structure)

    for hubbard_atom in hubbard_atoms:
        hubbard_structure.initialize_onsites_hubbard(
            hubbard_atom, *hubbard_dict[hubbard_atom]
        )
        hubbard_structure.initialize_intersites_hubbard(
            atom_name=hubbard_atom,
            atom_manifold=hubbard_dict[hubbard_atom][0],
            neighbour_name="O",
            neighbour_manifold="2p",
            value=0.0001,
        )

    return hubbard_structure
