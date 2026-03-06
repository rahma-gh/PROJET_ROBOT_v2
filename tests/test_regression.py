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
    # Laisser la scène s'initialiser complètement
    for _ in range(5):
        _pr.step()
    yield _pr
    _pr.stop()
    _pr.shutdown()


def test_csv_presence():
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant !"


def test_load_positions_format():
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6


def test_list_scene_objects(pr):
    """
    Diagnostic : liste tous les objets de la scène avec simGetObjectHandle
    en essayant des noms courants, plus un scan par index.
    """
    print("\n=== Scan par index ===")
    found = []
    for idx in range(500):
        handle = sim_backend.lib.simGetObjects(idx, -1)  # -1 = sim_handle_all
        if handle == -1:
            break
        found.append(handle)
        print(f"  handle={handle}")

    print(f"\n=== Test noms courants ===")
    candidates = [
        'UR10', 'ur10', 'UR10_base', 'UR10#0',
        'robot', 'Robot', 'Manipulator',
        'vacuum_gripper', 'VacuumGripper', 'Gripper',
        'ConveyorSensor', 'Cartoons1',
        'ikTip', 'ikTarget', 'joint1',
    ]
    for name in candidates:
        h = sim_backend.lib.simGetObjectHandle(name.encode('ascii'))
        status = f"handle={h}" if h >= 0 else "NOT FOUND"
        print(f"  '{name}' → {status}")

    print(f"\nTotal objets par index: {len(found)}")
    # Ce test est purement informatif
    assert True