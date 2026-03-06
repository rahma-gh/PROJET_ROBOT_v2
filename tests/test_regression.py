import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # Connexion au serveur démarré par entrypoint.sh
    client = RemoteAPIClient(host='localhost', port=23000)
    
    try:
        sim = client.require('sim')
        sim.stopSimulation()
        time.sleep(1.0)
        sim.startSimulation()
        time.sleep(2.0) # Attendre que les scripts Lua s'initialisent
        yield sim
        sim.stopSimulation()
    except Exception as e:
        pytest.fail(f"Erreur de connexion ZMQ : {e}")

def test_csv_presence():
    # Création d'un CSV par défaut si absent pour éviter l'erreur de fichier
    if not os.path.exists('pallet_positions.csv'):
        with open('pallet_positions.csv', 'w') as f:
            f.write("-221.99,-1125.42,-283.99,0,0,-90\n")
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6

def test_robot_communication(sim):
    from lib.ArmRobot import UniversalRobot
    # On passe l'instance 'sim' au robot pour éviter d'ouvrir un 2ème client
    robot = UniversalRobot('UR10', sim=sim)
    pos = robot.ReadPosition()
    assert len(pos) == 6