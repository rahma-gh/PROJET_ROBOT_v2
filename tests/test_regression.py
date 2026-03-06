import os
import pytest
from pyrep import PyRep
from pyrep.objects.object import Object

SCENE_FILE = os.path.join(os.path.dirname(__file__), '..', 'pick_and_place.ttt')


# ── Fixture PyRep ────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def pr():
    _pr = PyRep()
    _pr.launch(SCENE_FILE, headless=True)
    _pr.start()
    yield _pr
    _pr.stop()
    _pr.shutdown()


# ── Tests ────────────────────────────────────────────────────────────────────

def test_csv_presence():
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant !"


def test_load_positions_format():
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6


def test_list_scene_objects(pr):
    """
    Diagnostic : liste tous les objets de la scène pour trouver
    le vrai nom du robot UR10 et du gripper.
    """
    from pyrep.const import ObjectType
    objects = pr.get_objects_in_tree(object_type=ObjectType.ALL)
    names = [obj.get_name() for obj in objects]
    print("\n=== Objets dans la scène ===")
    for name in sorted(names):
        print(f"  - {name}")
    print("============================\n")
    # Ce test passe toujours — il sert juste à afficher les noms
    assert len(names) > 0, "Aucun objet trouvé dans la scène"


def test_robot_and_scene(pr):
    # Sera corrigé après avoir vu les vrais noms dans test_list_scene_objects
    pass


def test_gripper_init(pr):
    # Sera corrigé après avoir vu les vrais noms dans test_list_scene_objects
    pass