from aiida import orm
from aiida.engine import ToContext, WorkChain, append_, if_, while_
from aiida.plugins import CalculationFactory, DataFactory, WorkflowFactory
from aiida_quantumespresso.workflows.protocols.utils import ProtocolMixin
from aiida_quantumespresso_hp.workflows.hubbard import SelfConsistentHubbardWorkChain

HubbardStructureData = DataFactory("quantumespresso.hubbard_structure")
StructureData = DataFactory("core.structure")

PwCalculation = CalculationFactory("quantumespresso.pw")

PwBaseWorkChain = WorkflowFactory("quantumespresso.pw.base")
PwRelaxWorkChain = WorkflowFactory("quantumespresso.pw.relax")

# ? Will we use the SelfConsistentHubbardWorkChain?
# HpWorkChain = WorkflowFactory("quantumespresso.hp")


class InsertionWorkChain(WorkChain):
    """Lets see if I'll manage to write the ion-insertion algorithm as a workchain.

    Args:
        WorkChain (WorkChain): Inheritance from the WorkChain class.
    """

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # ? Which one of the two?
        # spec.input("hubbard_structure", valid_type=HubbardStructureData)
        spec.input("structuredata", valid_type=orm.StructureData)

        # ? Alternatively max_iterations
        # spec.input(
        #     "max_lithiation",
        #     valid_type=orm.Float,
        #     default=lambda: orm.Float(1),  # ? Where here lambda funciton?
        #     help=("Maximum lithiation until which the algorithm will be run."),
        #     required=False,
        # )

        # spec.expose_inputs(
        #     PwRelaxWorkChain,
        #     namespace="relax",
        #     exclude=("structure",),
        #     namespace_options={
        #         "required": False,
        #         "populate_defaults": False,
        #         "help": "Inputs for the `PwRelaxWorkChain` that, when defined, will iteratively relax the structure.",
        #     },
        # )
        # spec.expose_inputs(PwBaseWorkChain, namespace="scf", exclude=("pw.structure",))
        # spec.expose_inputs(
        #     SelfConsistentHubbardWorkChain,
        #     namespace="scf_hubbard",
        #     # ? not sure what this does
        #     # exclude=(
        #     #     "hp.parent_scf",
        #     #     "hp.hubbard_structure",
        #     # ),
        # )

        # spec.input(
        #     "clean_workdir",
        #     valid_type=orm.Bool,
        #     default=lambda: orm.Bool(True),
        #     help="If `True`, work directories of all called calculation will be cleaned at the end of execution.",
        # )

        spec.outline(
            cls.setup,
            # while_(cls.should_run_iteration)(
            #     pass
            #     cls.update_iteration,
            #     if_(cls.should_run_relax)(
            #         cls.run_relax,
            #         cls.inspect_relax,
            #     ),
            #     cls.run_scf_smearing,
            #     cls.recon_scf,
            #     if_(cls.is_insulator)(
            #         cls.run_scf_fixed,
            #         cls.inspect_scf,
            #     ),
            #     cls.run_hp,
            #     cls.inspect_hp,
            #     cls.check_convergence,
            # ),
            # cls.run_results,
        )

        # spec.output(
        #     "global_minimum",
        #     valid_type=StructureData,
        #     required=False,
        #     help="The Hubbard structure containing the structure and the Hubbard parameters, joined together.",
        # )
        # spec.output_namespace(
        #     "hubbard_structures",
        #     valid_type=orm.Dict,
        #     required=False,
        #     help="The HubbardStructureData of each iteration of the self-consistent cycle.",
        # )

    def setup(self):
        """Placeholder."""

        self.ctx.iteration = 0

        # region
        # # Set ctx variables for the cycle.
        # self.ctx.current_hubbard_structure = self.inputs.hubbard_structure
        # self.ctx.current_magnetic_moments = None  # starting_magnetization dict for collinear spin calcs
        # self.ctx.is_converged = False
        # self.ctx.is_insulator = None
        # self.ctx.skip_first_relax = self.inputs.skip_first_relax

        # # Determine whether the system is to be treated as magnetic
        # parameters = self.inputs.scf.pw.parameters.get_dict()
        # nspin = parameters.get('SYSTEM', {}).get('nspin', self.defaults.qe.nspin)
        # if nspin == 1:
        #     self.report('system is treated to be non-magnetic because `nspin == 1` in `scf.pw.parameters` input.')
        #     self.ctx.is_magnetic = False
        # else:
        #     self.report('system is treated to be magnetic because `nspin != 1` in `scf.pw.parameters` input.')
        #     self.ctx.is_magnetic = True
        #     if nspin == 2:
        #         magnetic_moments = parameters.get('SYSTEM', {}).get('starting_magnetization', None)
        #         if magnetic_moments is None:
        #             raise NameError('Missing `starting_magnetization` input in `scf.pw.parameters` while `nspin == 2`.')
        #         self.ctx.current_magnetic_moments = orm.Dict(magnetic_moments)
        #     else:
        #         raise NotImplementedError(f'nspin=`{nspin}` is not implemented in the `hp.x` code.')
        # endregion

    def run_results(self):
        """Attach the final converged Hubbard U parameters and the corresponding structure."""
        self.report(
            "Generated {} structures. Up to a lithiation of: {}.".format(
                self.ctx.iteration, self.inputs.max_lithiation
            )
        )
        self.out("hubbard_structure", self.ctx.current_hubbard_structure)
        # self.out('hubbard', self.ctx.workchains_hp[-1].outputs.hubbard)


# spec.input()
# spec.expose_inputs()

# spec.outline()
# spec.output()
# spec.output_namespace()

# spec.exit_code()

# spec.inputs


class OutputInputWorkchain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)

        spec.input("x", valid_type=orm.Int)
        spec.outline(cls.result)
        spec.output("workchain_result", valid_type=orm.Int)

    def result(self):
        self.out("workchain_result", self.inputs.x)


# run_number = 0

if __name__ == "__main__":

    from aiida import load_profile
    from aiida.engine import run
    from aiida.orm import load_code, load_node

    load_profile()

    # pw_code = load_code(2182)
    # hp_code = load_code(2183)

    structuredata = load_node(7209)

    print("test")
    insertion_workchain = run(InsertionWorkChain, structuredata=structuredata)
    print("test")
    # (
    #         structuredata=structuredata,
    # max_lithiation=orm.Float(1.0),
    #     )
    # )

    # result = run(OutputInputWorkchain, x=orm.Int(1))
    outputinputworkchain = run(OutputInputWorkchain, x=orm.Int(1))

    # print(result)
