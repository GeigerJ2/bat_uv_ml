from aiida.orm import StructureData
from ase.atoms import Atoms
from project_data import *
from project_data import DEFAULT_BUILDER_DICT, GLOBAL_SYMPREC, HUBBARD_DICT
from pyconfsamp.core import ConfigClass


def run_full_sampling(
    short_name,
    cell_size,
    ase_structure,
    group_label,
    relax_option,
    submit_index: int = None,
):
    config_class = ConfigClass()
    # ! Does not take into account initial magmoms for now
    # ? Don't need to do sorting anymore. Is done inside aiida-hp.
    # ase_structure = Atoms(
    #     sorted(ase_structure, key=lambda x: SORTING_DICT[x.symbol]),
    #     cell=ase_structure.get_cell(),
    #     pbc=True,
    # )
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
    config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    # ? Generate Builders
    config_class.generate_builders(
        builder_dict=DEFAULT_BUILDER_DICT,
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
