import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

@pytest.fixture(scope="session")
def sim():
    client = RemoteAPIClient(host='localhost', port=23000)
    try:
        sim = client.require('sim')
        sim.startSimulation()
        yield sim
        sim.stopSimulation()
    except Exception as e:
        pytest.fail(f"Connexion ZMQ échouée : {e}")

def test_csv_presence():
    assert os.path.exists('pallet_positions.csv')

def test_robot_logic(sim):
    from lib.ArmRobot import UniversalRobot
    # On passe sim=sim ! C'est le secret.
    robot = UniversalRobot('UR10', sim=sim)
    pos = robot.ReadPosition()
    assert len(pos) == 6