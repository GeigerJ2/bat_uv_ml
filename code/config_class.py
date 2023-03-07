import importlib
import os
from pprint import pprint
from typing import List, Optional, TypeVar, Union

import pandas as pd
from ase.atoms import Atoms
from project_settings import project_dir
from pybat.core import Cathode

# importlib.reload(Cathode)
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from sklearn.ensemble import RandomForestRegressor

GLOBAL_SYMPREC = 1e-5


# class ConfigSet:
# """Class which holds a set of configurations for a given cathode."""

# def __init__(
#     self,
#     name=None,
#     cell_size: int = 1,
#     symprec: float = 1e-5,
#     parent_spacegroup: tuple = None,
#     configuration_list: Optional[List[int]] = None,
#     cathode: Cathode = None,
#     ase_structure: Atoms = None,
#     pmg_structure: Structure = None,
# ):
#     self.name = name
#     self.cell_size = cell_size
#     self.symprec = symprec
#     self.parent_spacegroup = parent_spacegroup
#     self.cathode = cathode
#     self.ase_structure = ase_structure
#     self.pmg_structure = pmg_structure

#     if configuration_list is None:
#         self.configuration_list = []

# def add_cathode(self, structure: Union[Structure, Atoms]) -> None:
#     """Add cathod structure to class instance.

#     Args:
#         structure (Union[Structure, Atoms]): Input structure as ase.Atoms or pymatgen.Structure.
#     """
#     if isinstance(structure, Structure):
#         self.cathode = Cathode.from_structure(structure)
#     elif isinstance(structure, Atoms):
#         self.cathode = Cathode.from_structure(
#             AseAtomsAdaptor.get_structure(structure)
#         )

# def __str__(self):
#     # TODO: Formula unit if self.ase_structure or self.pmg_structure is set.
#     return "Name: {} | Size: {}".format(self.name, self.cell_size)

# def __repr__(self):
#     # TODO
#     pass

# def change_ion(self, old_ion: str = "Li", new_ion: str = "Na"):
#     # TODO
#     pass

# def get_cation_configurations(self, **kwargs):
#     self.configuration_list = self.cathode.get_cation_configurations(**kwargs)

# def get_parent_spacegroup_(self):
#     return self.cathode.get_space_group_info(symprec=GLOBAL_SYMPREC)


class ConfigSet(Cathode, Structure):
    """Class which holds a set of configurations for a given cathode."""

    def __init__(
        self,
        # All the stuff needed for Structure/Cathode init file
        lattice,
        species,
        coords,
        charge=None,
        validate_proximity=False,
        to_unit_cell=False,
        coords_are_cartesian=False,
        site_properties=None,
        # My own attributes
        name=None,
        cell_size: int = 1,
        symprec: float = 1e-5,
        parent_spacegroup: tuple = None,
        configuration_list: Optional[List[int]] = None,
        cathode: Cathode = None,
        ase_structure: Atoms = None,
        pmg_structure: Structure = None,
    ):
        super().__init__(lattice=lattice, species=species, coords=coords, charge=charge,
            validate_proximity=validate_proximity,
            to_unit_cell=to_unit_cell,
            coords_are_cartesian=coords_are_cartesian,
            site_properties=site_properties,)
        self.name = name
        self.cell_size = cell_size
        self.symprec = symprec
        self.parent_spacegroup = parent_spacegroup
        self.cathode = cathode
        self.ase_structure = ase_structure
        self.pmg_structure = pmg_structure

        if configuration_list is None:
            self.configuration_list = []

    @classmethod
    def from_cathode(cls, cathode) -> None:
        return cls.from_sites(cathode.sites)

    # @classmethod
    # def from_structure(cls, structure) -> None:
    #     return cls.from_sites(structure.sites)

    def __str__(self):
        # TODO: Formula unit if self.ase_structure or self.pmg_structure is set.
        return "Name: {} | Size: {}".format(self.name, self.cell_size)

    def __repr__(self):
        # TODO
        pass

    def change_ion(self, old_ion: str = "Li", new_ion: str = "Na"):
        # TODO
        pass

    def get_cation_configurations(self, **kwargs):
        self.configuration_list = self.cathode.get_cation_configurations(**kwargs)

    def get_parent_spacegroup_(self):
        return self.cathode.get_space_group_info(symprec=GLOBAL_SYMPREC)


if __name__ == "__main__":
    print("=" * 100, "\nRUN")
    fully_lithiated_df = pd.read_pickle(
        os.path.join(project_dir, "data", "fully_lithiated_df.pkl")
    )

    # Setup of configuration sampling
    devel_ase = fully_lithiated_df["ase_in"].values[0]
    devel_pmg = fully_lithiated_df["pmg_in"].values[0]
    devel_cathode = Cathode.from_structure(devel_pmg)
    devel_config_dict = dict(
        substitution_sites=list(range(0, devel_ase.get_chemical_symbols().count("Li"))),
        cation_list=["Li", "Vac"],
        sizes=[1],
        concentration_restrictions={"Li": (0, 1)},
        max_configurations=None,
        symprec=GLOBAL_SYMPREC,
    )

    config_set_1 = ConfigSet.from_cathode(devel_cathode)


    # config_set.name = "LFPO"
    # config_set.cell_size = 2
    # config_set.add_cathode(structure=devel_ase)
    # config_set.get_cation_configurations(**devel_config_dict)
    # config_set.parent_spacegroup = config_set.get_parent_spacegroup_()

    # print(config_set.parent_spacegroup)
    # print(len(config_set.configuration_list))


    # config_set = ConfigSet()
    # config_set.name = "LFPO"
    # config_set.cell_size = 2
    # config_set.add_cathode(structure=devel_ase)
    # config_set.get_cation_configurations(**devel_config_dict)
    # config_set.parent_spacegroup = config_set.get_parent_spacegroup_()

    # config_set = ConfigSet.from_structure(devel_structure)