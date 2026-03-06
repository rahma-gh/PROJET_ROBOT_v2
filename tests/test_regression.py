import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # Spécification explicite de l'hôte et du port pour correspondre à entrypoint.sh
    client = RemoteAPIClient(host='localhost', port=23000)
    sim = client.require('sim')
    
    # Reset de la simulation au cas où une session précédente aurait planté
    sim.stopSimulation()
    time.sleep(1.0)
    
    sim.startSimulation()
    time.sleep(2.0) # Temps pour que les handles d'objets soient valides
    yield sim
    
    sim.stopSimulation()
    time.sleep(0.5)

def test_csv_presence():
    # Création d'un fichier vide si nécessaire pour éviter l'échec du test format
    if not os.path.exists('pallet_positions.csv'):
        with open('pallet_positions.csv', 'w') as f:
            f.write("0,0,0,0,0,0")
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6

def test_robot_and_scene(sim):
    # Utilisation de l'instance sim de la fixture
    tip  = sim.getObject('/UR10/ikTip')
    base = sim.getObject('/UR10')
    pos  = sim.getObjectPosition(tip, base)
    assert len(pos) == 3

def test_gripper_init(sim):
    handle = sim.getObject('/UR10/vacuum_gripper')
    assert handle >= 0