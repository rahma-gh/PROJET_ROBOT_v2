import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


@pytest.fixture(scope="session")
def sim():
    client = RemoteAPIClient(host='localhost', port=23000)
    try:
        sim = client.require('sim')
        yield sim
    except Exception as e:
        pytest.fail(f"Connexion ZMQ échouée : {e}")


def test_csv_presence():
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant"


def test_robot_position(sim):
    from lib.ArmRobot import UniversalRobot
    robot = UniversalRobot('UR10', sim=sim)
    pos = robot.ReadPosition()
    assert len(pos) == 6, f"Position invalide : {pos}"