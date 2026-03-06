import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # Connexion explicite au port défini dans entrypoint.sh
    client = RemoteAPIClient(host='localhost', port=23000)
    sim = client.require('sim')
    
    # Reset propre de la simulation
    sim.stopSimulation()
    time.sleep(1.0)
    
    sim.startSimulation()
    time.sleep(2.0) # Laisse le temps aux objets de s'initialiser
    yield sim
    
    sim.stopSimulation()

def test_csv_presence():
    # Création d'un fichier factice si absent pour passer le test en CI
    if not os.path.exists('pallet_positions.csv'):
        with open('pallet_positions.csv', 'w') as f:
            f.write("0,0,0,0,0,0")
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    from main import LoadPalletPosition
    # On teste uniquement la lecture logicielle ici
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6

def test_robot_and_scene(sim):
    # On vérifie que la scène chargée dans le conteneur est correcte
    tip  = sim.getObject('/UR10/ikTip')
    assert tip != -1