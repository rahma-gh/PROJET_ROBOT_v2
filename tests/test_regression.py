import os
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
from lib.ArmRobot import UniversalRobot


@pytest.fixture(scope="session")
def sim():
    client = RemoteAPIClient(host='localhost', port=23000)
    sim = client.require('sim')
    sim.startSimulation()
    time.sleep(2.0)
    yield sim
    sim.stopSimulation()
    time.sleep(0.5)


def test_csv_presence():
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant !"


def test_load_positions_format(sim):
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0
    assert len(positions[0]) == 6


def test_robot_and_scene(sim):
    tip = sim.getObject('/UR10/ikTip')
    base = sim.getObject('/UR10')
    pos = sim.getObjectPosition(tip, base)
    assert len(pos) == 3


def test_gripper_init(sim):
    handle = sim.getObject('/UR10/vacuum_gripper')
    assert handle >= 0