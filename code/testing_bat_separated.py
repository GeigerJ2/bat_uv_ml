# %%
import pathlib

import pandas as pd
from aiida import load_profile
from aiida.engine import submit
from aiida.orm import load_node
from aiida.plugins import DataFactory
from aiida_quantumespresso.common.types import SpinType
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from project_data import *

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

pk_list = [58659, 58660, 58661, 58662, 58663]
name_list = ["lfpo", "lfmpo", "lmpo", "lmno", "lmo"]

# %% #? Try out all with a bunch of options

for name, pk in list(zip(name_list, pk_list)):
    # if name in ["lfpo", "lfmpo", "lmpo"]:
    # if name in ["lfpo", "lfmpo"]:
    builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
        pw_code=PW_CODE_LUMI,
        hp_code=HP_CODE_LUMI,
        hubbard_structure=load_node(pk),
        protocol="moderate",
        overrides=pathlib.Path(
            "/home/jgeiger/projects/bat_uv_ml/code/yaml_files/iurii_overrides/{}.yaml".format(
                name
            )
        ),
        spin_type=SpinType.COLLINEAR,
    )

    # builder.relax.base.pw.parameters["ELECTRONS"]["mixing_beta"] = 0.1
    # builder.scf.pw.parameters["ELECTRONS"]["mixing_beta"] = 0.1

    # builder.relax.base.pw.parameters["SYSTEM"] = AttributeDict(
    #     {"smearing": "gauss", "degauss": 0.05}
    # )
    # builder.scf.pw.parameters["SYSTEM"] = AttributeDict(
    #     {"smearing": "gauss", "degauss": 0.05}
    # )

    # builder.relax.base.pw.parameters["IONS"] = AttributeDict(
    #     {"trust_radius_min": 1e-4, "bfgs_ndim": 8}
    # )

    # builder.relax.base.pw.parameters["IONS"] = AttributeDict(
    #     {"ion_dynamics": "damp"}
    # )

    # ? Defaults:  "conv_thr": 5.6e-09, "etot_conv_thr": 0.00028, "forc_conv_thr": 0.0001
    # builder.relax.base.pw.parameters["CONTROL"]["etot_conv_thr"] = 0.0028
    # builder.relax.base.pw.parameters["CONTROL"]["forc_conv_thr"] = 0.001
    # builder.relax.base.pw.parameters["ELECTRONS"]["conv_thr"] = 5.6e-8
    builder.hubbard.hp.parameters["INPUTHP"]["dist_thr"] = 100
    # builder.skip_first_relax = True
    # builder.hubbard.hp.parameters["INPUTHP"]["docc_thr"] = 1e-15

    submit_node = submit(builder)
    submit_node.label = "{}_iurii_resub_dist_thr".format(name)
    print(name, submit_node.pk)