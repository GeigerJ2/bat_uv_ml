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


# %% # ? Develop changing the magnetization

_ = importlib.reload(pyconfsamp.core)

RELABEL_DICT = {
    0: "Mn0",
    1: "Mn0",
    2: "Mn1",
    3: "Mn1",
}

MAG_DICT = {
    "Mn0": 0.5,
    "Mn1": -0.5,
    # ? The following ones could be set via dict.get(default: 0.0)
    "O": 0.0,
    "P": 0.0,
    "Li": 0.0,
    # "nspin": 2,
}

for short_name, structure_data in list(zip(fully_lithiated_names, structure_datas))[
    2:3
]:
    config_class = pyconfsamp.core.ConfigClass()
    config_class.short_name = short_name
    magnetic_structure_data = structure_data.clone()
    # print(magnetic_structure_data.get_formula(mode="reduce"))
    # print(magnetic_structure_data.get_ase().get_chemical_symbols())
    # ! Now the relabelling needs to be done outside, as ASE and pymatgen internally don't like custom labels.
    magnetic_structure_data = pyconfsamp.core.change_atom_names(
        structure_data=magnetic_structure_data, relabel_dict=RELABEL_DICT
    )
    # print(magnetic_structure_data.get_formula(mode="reduce"))

    config_class.add_structuredata(structuredata=structure_data)
    config_class.cell_size = CELL_SIZE
    config_class.which_ones = "first"

    config_class.generate_configs(config_dict=CONFIG_DICT)
    config_class.generate_hubbards(hubbard_dict=HUBBARD_DICT)
    config_class.generate_builders(
        builder_dict=BUILDER_DICT, relax_option=OPTION, mag_dict=MAG_DICT
    )

    group_label = "testing/{}/{}".format(short_name, OPTION)
    print(group_label)
    config_class.submit_builders(group_label=group_label)

    # data_df = config_class.data_df()
    # # data_df.head()
    # data_df["pmg_structure"].values[0]

    break

# %%

config_class.generate_df()

# %% # ? Sort Atoms and store structuredatas


# sorting_dict = {
#     "Mn": 0,
#     "Fe": 1,
#     "Ni": 2,
#     "O": 3,
#     "P": 4,
#     "Li": 5,
# }

# ase_structures = fully_lithiated_df["ase_in"].values

# # ! Does not take into account initial magmoms for now
# ase_structures = [
#     Atoms(
#         sorted(ase_structure, key=lambda x: sorting_dict[x.symbol]),
#         cell=ase_structure.get_cell(),
#         pbc=True,
#     )
#     for ase_structure in ase_structures
# ]

# # sorted_ase_structure = ase_structure.center() for ase_structure in sorted_ase_structures]
# print([_.symbols for _ in ase_structures])
# _ = [ase_structure.center() for ase_structure in ase_structures]
# pmg_structures = [
#     AseAtomsAdaptor.get_structure(ase_structure) for ase_structure in ase_structures
# ]

# structure_datas = [
#     StructureData(pymatgen_structure=pmg_structure) for pmg_structure in pmg_structures
# _ = [structure_data.store() for structure_data in structure_datas]
# print([structure_data.pk for structure_data in structure_datas])
# cathode_structures = [
#     Cathode.from_structure(pmg_structure) for pmg_structure in pmg_structures
# ]

# %% # ? Former AFM magnetization setting for LMPO configurations


# structuredata = change_atom_names(
#     structure_data=structuredata, relabel_dict=relabel_dict
# )

# if "Li" in formula:
#     builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict
# else:
#     noli_mag_dict = deepcopy(afm_mag_dict)
#     noli_mag_dict["starting_magnetization"].pop("Li")
#     builder.scf.pw.parameters["SYSTEM"] = afm_mag_dict


# %% # ? Group loading
submission_group_label = "testing/lithiated_structures/option3/nomag"
try:
    submission_group = Group(submission_group_label)
    submission_group.store()
except:  # IntegrityError:
    submission_group = load_group(submission_group_label)

# %% # ? Initialize Hubbard
# hubbard_dict = {
#     "olivine": {"Mn": ("3d", 4.6), "Fe": ("3d", 5.3)},
#     "spinel": {"Mn": ("3d", 6.6), "Ni": ("3d", 8.6)},
# }

# %% # ? Actually running builder function and submitting

default_hubbard_dict = {
    "Mn": ("3d", 5.6),  # ? Average between 4.6 and 6.6
    "Fe": ("3d", 5.3),
    "Ni": ("3d", 8.6),
}

default_builder_dict = {
    "pw_code": pw_code,
    "hp_code": hp_code,
    "protocol": "moderate",
    "overrides": Path(os.path.join("yaml_files", "default_overrides.yaml")),
    "spin_type": SpinType.COLLINEAR,
}

# pattern = r"\b({})\b".format("|".join(map(test_string, hubbard_atoms)))
fully_lithiated_builders = []
for structure_data in structure_datas:
    print(structure_data.get_formula(mode="reduce"))
    builder = prepare_builder(
        structuredata=structure_data,
        option=3,
        hubbard_dict=default_hubbard_dict,
        builder_dict=default_builder_dict,
    )
    fully_lithiated_builders.append(builder)

    # builder_submit = submit(builder)
    # submission_group.add_nodes(builder_submit)


# %% # ? Builder

# default_builder_dict = {
#     "pw_code": pw_code,
#     "hp_code": hp_code,
#     "protocol": "moderate",
#     "overrides": Path(os.path.join("..", "yaml_files", "default_overrides.yaml")),
# }

# builder = SelfConsistentHubbardWorkChain.get_builder_from_protocol(
#     pw_code=pw_code,
#     hp_code=hp_code,
#     protocol="moderate",
#     overrides=Path(os.path.join("..", "yaml_files", "default_overrides.yaml")),
#     hubbard_structure=devel_hubbard_structure,
# )

# qpoints = KpointsData()
# qpoints.set_cell_from_structure(structuredata=devel_hubbard_structure)
# qpoints.set_kpoints_mesh_from_density(distance=1.2)

# builder.hubbard.hp.qpoints = qpoints
# devel_hubbard_structure.cell

# print(builder.hubbard.hp.qpoints.get_kpoints_mesh())

# ! option1
# _ = builder.pop("relax", None)
# builder.meta_convergence = Bool(False)
# builder.max_iterations = Int(1)
# ! option2
# _ = option2_builder.pop("relax", None)
# ! option3
