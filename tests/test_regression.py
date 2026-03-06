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
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant !"


def test_load_positions_format():
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6


def test_scene_is_loaded(pr):
    """
    Vérifie que la scène est réellement chargée en essayant de récupérer
    un objet par handle numérique (handle 0 = toujours la scène elle-même
    dans CoppeliaSim si la scène est chargée).
    Affiche aussi des infos de debug sur l'état de la simulation.
    """
    # 1. Vérifier l'état de la simulation
    sim_state = sim_backend.lib.simGetSimulationState()
    print(f"\nsimGetSimulationState() = {sim_state}")
    # 17 = simulation running, 0 = stopped
    assert sim_state > 0, f"Simulation non démarrée (state={sim_state})"

    # 2. Compter les objets dans la scène
    count = sim_backend.lib.simGetObjectsInTree(
        -1,   # sim_handle_scene = racine
        -1,   # tous types
        0,    # options
        None  # pas de filtre
    )
    print(f"simGetObjectsInTree count type = {type(count)}, value = {count}")

    # 3. Essayer de récupérer le handle de la scène elle-même
    scene_handle = sim_backend.lib.simGetInt32Parameter(2000)  # sim_intparam_scene_unique_id
    print(f"Scene unique ID = {scene_handle}")

    # 4. Tenter de trouver des objets par nom générique
    for name in ['DefaultCamera', 'DefaultLights', 'ResizableFloor_5_25']:
        h = sim_backend.lib.simGetObjectHandle(name.encode('ascii'))
        print(f"  '{name}' → handle={h}")

    # Si la simulation tourne, la scène est au moins partiellement chargée
    assert sim_state > 0


def test_robot_and_scene(pr):
    pass


def test_gripper_init(pr):
    pass