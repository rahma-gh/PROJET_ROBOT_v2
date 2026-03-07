import os
import zmq
import pytest
import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


@pytest.fixture(scope="session")
def sim():
    """
    Establish a ZMQ connection to CoppeliaSim with explicit timeout and retry.
    Without a recv_timeout the socket blocks forever; pytest-timeout then kills
    the whole test with an unhelpful error.
    """
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            client = RemoteAPIClient(host='localhost', port=23000)
            # Set a recv timeout so a hung simulator surfaces a clean error
            # instead of blocking until pytest-timeout fires.
            client.socket.setsockopt(zmq.RCVTIMEO, 15_000)  # 15 s
            sim = client.require('sim')
            yield sim
            return
        except Exception as e:
            if attempt == max_attempts:
                pytest.fail(
                    f"ZMQ connection failed after {max_attempts} attempts: {e}"
                )
            wait = attempt * 3
            print(f"\nAttempt {attempt} failed ({e}). Retrying in {wait}s...")
            time.sleep(wait)


def test_csv_presence():
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant"


def test_robot_position(sim):
    from lib.ArmRobot import UniversalRobot
    robot = UniversalRobot('UR10', sim=sim)
    pos = robot.ReadPosition()
    assert len(pos) == 6, f"Position invalide : {pos}"