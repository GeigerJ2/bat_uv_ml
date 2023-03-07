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
        super().__init__(
            lattice=lattice,
            species=species,
            coords=coords,
            charge=charge,
            validate_proximity=validate_proximity,
            to_unit_cell=to_unit_cell,
            coords_are_cartesian=coords_are_cartesian,
            site_properties=site_properties,
        )
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

# def __repr__(self):
#     # TODO
#     pass

# def change_ion(self, old_ion: str = "Li", new_ion: str = "Na"):
#     # TODO
#     pass