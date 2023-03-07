import importlib
import os
import re
from collections import Counter
from pprint import pprint
from typing import List, Optional, TypeVar, Union

import numpy as np
import pandas as pd
from ase.atoms import Atoms
from project_settings import project_dir
from pybat.core import Cathode

# importlib.reload(Cathode)
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from sklearn.ensemble import RandomForestRegressor


class ConfigSet:
    """Class which holds a set of configurations for a given cathode."""

    def __init__(
        self,
        short_name=None,
        cell_size: int = 1,
        symprec: float = 1e-5,
        configuration_list: Optional[List[int]] = None,
        cathode: Cathode = None,
        ase_structure: Atoms = None,
        pmg_structure: Structure = None,
        data_df: pd.DataFrame = None,
        _parent_sg: str = None,
        _parent_cv: str = None,
    ):
        self.short_name = short_name
        self.cell_size = cell_size
        self.symprec = symprec
        self.cathode = cathode
        self.ase_structure = ase_structure
        self.pmg_structure = pmg_structure
        self._parent_sg = _parent_sg
        self._parent_cv = _parent_cv
        self.data_df = data_df

        if configuration_list is None:
            self.configuration_list = []

    def add_structure(self, structure: Union[Structure, Atoms]) -> None:
        """
        Add cathode structure to class instance.

        # ? Not sure how to actually handle populating also ase and pmg objects here -> and probably unnecessary.

        Args:
            structure (Union[Structure, Atoms]): Input structure as ase.Atoms or pymatgen.Structure.
        """
        if isinstance(structure, Structure):
            self.cathode = Cathode.from_structure(structure)
        elif isinstance(structure, Atoms):
            self.cathode = Cathode.from_structure(
                AseAtomsAdaptor.get_structure(structure)
            )
        elif isinstance(structure, Cathode):
            self.cathode = structure

    # ! Some stuff related to the parent spacegroup, for learning about property, getters, and setters.
    # region Parent Spacegroup

    @property
    def parent_sg(self):
        return self._parent_sg

    def eval_parent_sg(self, symprec: float = 1e-5) -> None:
        self._parent_sg = self.cathode.get_space_group_info(symprec=symprec)[0]

    @parent_sg.setter
    def parent_sg(self, value):
        if type(value) == str:
            self._parent_sg = value

    @parent_sg.getter
    def parent_sg(self):
        return self._parent_sg

    @parent_sg.deleter
    def parent_sg(self):
        del self._parent_sg

    # endregion

    # @property
    # def parent_formula(self):
    #     return self._parent_sg

    def __str__(self):
        # TODO: Formula unit if self.ase_structure or self.pmg_structure is set.
        return "Name: {} | Size: {}".format(self.short_name, self.cell_size)

    def create_configurations(self, **configuration_dict):
        configuration_dict = {**configuration_dict, **{"sizes": [self.cell_size]}}
        configuration_list = self.cathode.get_cation_configurations(
            **configuration_dict
        )
        # ! Otherwise, for whichever reason, the fully lithiated configuration is missing
        # ! -> This might be intentional, as one can just calculate it in the smaller cell.
        # if self.cell_size > 1:
        #     configuration_list.append(self.cathode)

        self.configuration_list = configuration_list

        # ! Add fully lithited one manually if cell_size > 1, as it is missing otherwise.

    def create_dataframe(self):

        pmg_list = [
            cathode.as_ordered_structure() for cathode in self.configuration_list
        ]
        # ! Maybe don't mix too much ase and pmg inside here.
        ase_list = [AseAtomsAdaptor.get_atoms(pmg_) for pmg_ in pmg_list]
        formula_list = [
            ase_structure.get_chemical_formula() for ase_structure in ase_list
        ]
        cell_vector_list = [np.array2string(_.cell.todict()["array"]) for _ in ase_list]
        sg_list = [
            configuration.space_group(symprec=GLOBAL_SYMPREC)
            for configuration in self.configuration_list
        ]
        li_list = [_.get_chemical_symbols().count("Li") for _ in ase_list]
        max_li_number = self.cell_size * int(
            re.match("Li\d{1,2}", self.cathode.formula).group(0).strip("Li")
        )
        lithiation_list = np.array(li_list) / max_li_number

        # ? Still need to apply the multiplicity_dict
        li_multiplicity_dict = dict(Counter(li_list))
        cell_multiplicity_dict = dict(Counter(cell_vector_list))
        sg_multiplicity_dict = dict(Counter(sg_list))

        # ! Count the configuration index for each cell geometry
        config_index_list = []
        for num_structures in cell_multiplicity_dict.values():
            config_index_list += range(num_structures)

        # Put all the data into pandas df
        _data_df = pd.DataFrame()
        _data_df["short_name"] = [self.short_name] * len(self.configuration_list)
        _data_df["cell_size"] = self.cell_size
        _data_df["configuration"] = self.configuration_list
        _data_df["li_number"] = li_list
        _data_df["formula"] = formula_list
        _data_df["cell_vectors"] = cell_vector_list
        _data_df["space_group"] = sg_list
        _data_df["ase_structure"] = ase_list
        _data_df["lithiation"] = lithiation_list
        _data_df["config_index"] = config_index_list

        # _data_df['lithiation'] = _data_df['li_number'] / (len(kwargs['substitution_sites'])*kwargs['sizes'][0])

        # _data_df = _data_df.sort_values(by='lithiation', ascending=False)
        _data_df["li_mpc"] = _data_df["li_number"].map(li_multiplicity_dict)
        _data_df["cell_mpc"] = _data_df["cell_vectors"].map(cell_multiplicity_dict)
        _data_df["sg_mpc"] = _data_df["space_group"].map(sg_multiplicity_dict)
        _data_df["specific_name"] = (
            _data_df["short_name"]
            + "-"
            + _data_df["cell_size"].astype(str)
            + "-"
            + _data_df["lithiation"].astype(str)
            + "-"
            + _data_df["config_index"].astype(str)
        )
        print(_data_df["specific_name"])
        self.data_df = _data_df

# ==================================================================================================

if __name__ == "__main__":
    print("=" * 100)
    fully_lithiated_df = pd.read_pickle(
        os.path.join(project_dir, "data", "fully_lithiated_df.pkl")
    )

    # Setup of configuration sampling
    GLOBAL_SYMPREC = 1e-5
    devel_ase = fully_lithiated_df["ase_in"].values[0]
    devel_pmg = fully_lithiated_df["pmg_in"].values[0]
    devel_cathode = Cathode.from_structure(devel_pmg)

    # Set initial, general parameters
    config_set = ConfigSet()
    config_set.short_name = "LFPO"
    config_set.add_structure(devel_cathode)
    config_set.eval_parent_sg(symprec=GLOBAL_SYMPREC)
    config_set.cell_size = 2

    # Run configuration sampling
    devel_config_dict = dict(
        substitution_sites=list(range(0, devel_ase.get_chemical_symbols().count("Li"))),
        cation_list=["Li", "Vac"],
        concentration_restrictions={"Li": (0, 1)},
        max_configurations=None,
        symprec=GLOBAL_SYMPREC,
    )

    # Create df which is linked to the class instance
    config_set.create_configurations(**devel_config_dict)
    config_set.create_dataframe()
    print(config_set.data_df)
