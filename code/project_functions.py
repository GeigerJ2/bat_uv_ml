from aiida.orm import StructureData, load_node
from aiida_pyconfsamp.core import ConfigClass
from aiida_quantumespresso.data.hubbard_structure import HubbardStructureData
from ase.atoms import Atoms
from ase.visualize import view
from project_data import DEFAULT_BUILDER_DICT, DEFAULT_HUBBARD_DICT, GLOBAL_SYMPREC


def run_full_sampling(
    short_name,
    cell_size,
    ase_structure,
    group_label,
    relax_option,
    submit_index: int = None,
    builder_dict: dict = DEFAULT_BUILDER_DICT,
):
    config_class = ConfigClass()
    # ! Does not take into account initial magmoms for now

    ase_structure.center()
    structuredata = StructureData(ase=ase_structure)

    config_class.short_name = short_name
    config_class.add_structuredata(structuredata)
    config_class.cell_size = cell_size

    config_dict = dict(
        cation_list=["Li", "Vac"],
        concentration_restrictions={"Li": (0, 1)},
        max_configurations=None,
        symprec=GLOBAL_SYMPREC,
    )

    # ? Generate Configurations
    config_class.generate_configs(config_dict=config_dict)
    # ? Generate Hubbards
    config_class.generate_hubbards(hubbard_dict=DEFAULT_HUBBARD_DICT)
    # ? Generate Builders
    config_class.generate_builders(
        builder_dict=builder_dict,
        relax_option=relax_option,
        parallelization="atoms",
        clean_workdir=False,
    )

    # ? Submit Builders
    config_class.submit_builders(
        group_label=group_label,
        submit_index=submit_index,
    )
    # ? Create df which is linked to the class instance
    config_df = config_class.generate_df()
    # ? Save the df as a pickle file
    # config_class.write_df(
    #     file_path="/home/jgeiger/projects/bat_uv_ml/data",
    # )
    # # # ? Try pickling again
    # config_class.pickle_me(
    #     file_path="/home/jgeiger/projects/bat_uv_ml/data",
    # )

    return {"config_class": config_class, "config_df": config_df}


def view_structure_from_pk(pk):
    node = load_node(pk)
    # ! Implement properly with isinstance
    try:
        ase_structure = node.inputs.hubbard_structure.get_ase()
    except:
        raise
    view(ase_structure)
