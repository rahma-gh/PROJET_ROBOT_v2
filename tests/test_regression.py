import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    # On force l'hôte à localhost sur le port défini dans entrypoint.sh
    client = RemoteAPIClient(host='localhost', port=23000)
    
    # On laisse un peu de temps au serveur pour être totalement prêt
    time.sleep(5) 
    
    try:
        sim = client.require('sim')
        # On s'assure que la simulation est propre
        sim.stopSimulation()
        time.sleep(1)
        sim.startSimulation()
        yield sim
        sim.stopSimulation()
    except Exception as e:
        pytest.fail(f"Le client ZMQ n'a pas pu se connecter à CoppeliaSim: {e}")

def test_csv_presence():
    assert os.path.exists('pallet_positions.csv')

def test_load_positions_format(sim):
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0

def test_robot_communication(sim):
    from lib.ArmRobot import UniversalRobot
    # On injecte la connexion 'sim' pour ne pas bloquer le port ZMQ
    robot = UniversalRobot('UR10', sim=sim)
    pos = robot.ReadPosition()
    assert len(pos) == 6