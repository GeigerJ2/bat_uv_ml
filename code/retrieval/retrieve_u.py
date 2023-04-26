# %%
from pprint import pprint

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from aiida import load_profile
from aiida.orm import Group, QueryBuilder, load_node
from aiida_quantumespresso.common.hubbard import Hubbard, HubbardParameters
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from aiida_quantumespresso_hp.workflows.hp.main import HpWorkChain
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain
from ase.visualize import view
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"
load_profile()
# %%
qb = QueryBuilder()
_ = qb.append(
    Group,
    filters={"label": {"==": "new_scf_hub/lmpo-1/option1/fm"}},
    tag="group",
)
_ = qb.append(
    SelfConsistentHubbardWorkChain,
    with_group="group",
    tag="scf_hub_wc",
)
_ = qb.append(
    HpWorkChain,
    with_incoming="scf_hub_wc",
    tag="hp_wc",
)

# Valid keywordds
_ = qb.append(HubbardStructureData, with_incoming="hp_wc", tag="hubbbard_structure")

# qb.add_projection("hubbbard_structure")
print(qb.count())

lmpo_hubbards = qb.all()


# %%


def retrieve_uv(
    hubbardstructuredata,
):
    hubbard_parameters = hubbardstructuredata.hubbard.parameters

    df_columns = [
        "atom_index",
        "atom_manifold",
        "neighbour_index",
        "neighbour_manifold",
        "value",
        "translationr",
        "hubbard_type",
    ]

    hubbard_tuple_list = [hubbard_parameter.to_tuple() for hubbard_parameter in hubbard_parameters]

    hubbard_df = pd.DataFrame(data=hubbard_tuple_list, columns=df_columns)
    u_df = hubbard_df.loc[hubbard_df["atom_index"] == hubbard_df["neighbour_index"]]
    v_df = hubbard_df.loc[hubbard_df["atom_index"] != hubbard_df["neighbour_index"]]

    u_avg = u_df["value"].mean()
    u_std = u_df["value"].std()

    v_avg = v_df["value"].mean()
    v_std = v_df["value"].std()

    return {"u_avg": u_avg, "u_std": u_std, "v_avg": v_avg, "v_std": v_std}

    # devel_hubbard_fig = px.scatter(data_frame=hubbard_df, x="atom_index", y="value")
    # devel_hubbard_fig.show()


ase_structures = []
for lmpo_hubbard in lmpo_hubbards:
    uv_dict = retrieve_uv(hubbardstructuredata=lmpo_hubbard[0])
    pprint(uv_dict)
    ase_structures.append(lmpo_hubbard[0].get_ase())
# view(ase_structures)

# %%

lmpo_workchains_qb = QueryBuilder()
_ = lmpo_workchains_qb.append(
    Group,
    filters={"label": {"==": "new_scf_hub/lmpo-1/option1/fm"}},
    tag="group",
)
_ = lmpo_workchains_qb.append(
    SelfConsistentHubbardWorkChain,
    with_group="group",
    tag="scf_hub_wc",
)
lmpo_workchains_qb.count()
# _ = workchain_qb.append(
#     HpWorkChain,
#     with_incoming="scf_hub_wc",
#     tag="hp_wc",
# )

# Valid keywordds
_ = lmpo_workchains_qb.append(HubbardStructureData, with_incoming="scf_hub_wc", tag="hubbbard_structure")

# qb.add_projection("hubbbard_structure")
lmpo_workchains_qb.all()


# %%
first_lmpo_workchain = lmpo_workchains_qb.first()[0]
print(first_lmpo_workchain)

input_hubbardstructuredata = load_node(39260)
output_hubbardstructuredata = load_node(39283)

for lmpo_hubbard in lmpo_hubbards[:1]:
    print(type(lmpo_hubbard[0]))
    print(lmpo_hubbard[0])
    pprint([_ for _ in dir(lmpo_hubbard[0]) if not _.startswith("_")])
    print(lmpo_hubbard[0].creator)


# retrieve_uv(input_hubbardstructuredata)

# print(input_hubbardstructuredata.hubbard)
# print(output_hubbardstructuredata)
print(retrieve_uv(input_hubbardstructuredata))
print(retrieve_uv(output_hubbardstructuredata))

# %% Get all structuredata objects within one exemplary selfconsistenthubbardworkchain

single_qb = QueryBuilder()
_ = single_qb.append(
    SelfConsistentHubbardWorkChain,
    filters={"id": {"==": 39266}},
    tag="single_workchain",
)
# _ = single_qb.append(
#     HubbardStructureData,
#     with_incoming="single_workchain",
# )
print(single_qb.count())

selfconsistenthubbardworkchain = single_qb.first()[0]
selfconsistenthubbardworkchain

selfconsistenthubbardworkchain.get_outgoing(node_class=HubbardStructureData).all_nodes()
selfconsistenthubbardworkchain.get_incoming(node_class=HubbardStructureData).all_nodes()
# selfconsistenthubbardworkchain.get_incoming().all_nodes()

# %%

for link_triple in selfconsistenthubbardworkchain.get_incoming().all():
    print(link_triple.node, link_triple.link_type, link_triple.link_label)

# %%
# query.append(
#     Group, filters={"label": {"like": "tutorial%"}}, project="label", tag="group"
# )
# # Retrieve every PwCalculation that is a member of the specified groups:
# query.append(PwCalculation, tag="calculation", with_group="group")
#
# query.append(
#     StructureData,
#     project=["extras.formula"],
#     tag="structure",
#     with_outgoing="calculation",
# )  # Complete the function call with the correct relationship-tag!
#
# query.append(
#     Dict,
#     tag="results",
#     project=[
#         "attributes.energy_smearing",
#         "attributes.energy_smearing_units",
#         "attributes.total_magnetization",
#         "attributes.total_magnetization_units",
#     ],
#     with_incoming="calculation",
# )
#
# results = query.all()
#
# for item in results:
#     print(", ".join(map(str, item)))
#
# plot_results(results)
