# %%
from aiida import load_profile
from aiida.orm import load_node
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = "all"

load_profile()

# %%
selfconsistenthubbardworkchain = load_node(25487)
