# For executing simple commands
# %%
from aiida import load_profile
from aiida.orm import StructureData, load_node
from aiida.plugins import DataFactory

AttributeDict = DataFactory("core.dict")

load_profile()


# %%
node = load_node(54175)
node_inputs = node.inputs

# hubbard_inputs = node_inputs.hubbard.convert()
hp_parameters = node_inputs.hubbard.hp.parameters.get_dict()
print(hubbard_inputs)
