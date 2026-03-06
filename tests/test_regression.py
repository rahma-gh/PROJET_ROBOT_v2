import os
import pytest
from pyrep import PyRep
from pyrep.backend import sim as sim_backend

SCENE_FILE = os.path.join(os.path.dirname(__file__), '..', 'pick_and_place.ttt')


@pytest.fixture(scope="session")
def pr():
    _pr = PyRep()
    _pr.launch(SCENE_FILE, headless=True)
    _pr.start()
    for _ in range(10):
        _pr.step()
    yield _pr
    _pr.stop()
    _pr.shutdown()


def test_csv_presence():
    assert os.path.exists('pallet_positions.csv')


def test_load_positions_format():
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6


def test_scene_is_loaded(pr):
    # Simulation running (17 = running)
    sim_state = sim_backend.lib.simGetSimulationState()
    print(f"\nsimGetSimulationState() = {sim_state}")
    assert sim_state == 17, f"Simulation non démarrée (state={sim_state})"

    # PyRep utilise cffi — les pointeurs se créent avec ffi
    from pyrep.backend.sim import ffi

    count_ptr = ffi.new('int *', 0)
    handles_ptr = sim_backend.lib.simGetObjectsInTree(
        -1,       # sim_handle_scene = toute la scène
        -1,       # tous types d'objets
        0,        # options
        count_ptr
    )
    count = count_ptr[0]
    print(f"Nombre d'objets dans la scène : {count}")

    if count > 0 and handles_ptr != ffi.NULL:
        print("\n=== Objets dans la scène ===")
        for i in range(count):
            handle = handles_ptr[i]
            name_ptr = sim_backend.lib.simGetObjectName(handle)
            if name_ptr != ffi.NULL:
                name = ffi.string(name_ptr).decode('utf-8')
                print(f"  handle={handle:4d}  name='{name}'")
        print("============================\n")

    assert count > 0, f"Scène vide — 0 objets trouvés (fichier .ttt incompatible avec CoppeliaSim 4.1 ?)"


def test_robot_and_scene(pr):
    pass


def test_gripper_init(pr):
    pass