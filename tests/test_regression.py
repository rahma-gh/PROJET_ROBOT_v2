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
    Diagnostic : liste tous les objets via l'API sim bas niveau.
    """
    print("\n=== Objets dans la scène ===")
    found = []
    # simGetObjectHandle retourne -1 si l'objet n'existe pas
    # On itère sur les handles avec simGetObjects
    idx = 0
    while True:
        # objectType=-1 = tous types, index=idx
        handle = sim_backend.lib.simGetObjects(idx, -1)
        if handle < 0:
            break
        try:
            name = sim_backend.lib.simGetObjectName(handle)
            if name:
                import ctypes
                name_str = ctypes.cast(name, ctypes.c_char_p).value.decode('utf-8')
                found.append(name_str)
                print(f"  [{idx}] handle={handle} name={name_str}")
        except Exception as e:
            print(f"  [{idx}] handle={handle} error={e}")
        idx += 1

    print(f"Total: {len(found)} objets")
    print("============================\n")
    assert len(found) > 0, "Aucun objet trouvé dans la scène"


def test_robot_and_scene(pr):
    pass


def test_gripper_init(pr):
    pass