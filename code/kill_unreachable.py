from aiida import load_profile
from aiida.manage.manager import get_manager

load_profile()

controller = get_manager().get_process_controller()
pks = [
    5883,
    6874,
    6893,
    7016,
    7035,
    7054,
    7073,
    7162,
    7199,
    7423,
    7461,
    7499,
    7537,
    7575,
    7613,
    7646,
    7684,
    7722,
    7760,
    7795,
    7828,
    7866,
    7903,
    7943,
    9073,
]  # Add the pks to this list of the processes that have become unreachable. Warning do **not** add processes that are actually running and are reachable
for pk in pks:
    controller.continue_process(pk, no_reply=True, nowait=True)
