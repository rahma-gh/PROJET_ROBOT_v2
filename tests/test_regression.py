import os
import pytest
from pyrep import PyRep
from lib.ArmRobot import UniversalRobot

SCENE_FILE = os.path.join(os.path.dirname(__file__), '..', 'pick_and_place.ttt')


# ── Fixture unique PyRep ─────────────────────────────────────────────────────
# PyRep lance CoppeliaSim en interne dans le même processus Python.
# Pas de ZMQ, pas de socket, pas de timeout possible.

@pytest.fixture(scope="session")
def pr():
    _pr = PyRep()
    _pr.launch(SCENE_FILE, headless=True)
    _pr.start()
    yield _pr
    _pr.stop()
    _pr.shutdown()


@pytest.fixture(scope="session")
def robot(pr):
    r = UniversalRobot('UR10', pr)
    r.AttachGripper('vacuum_gripper')
    return r


# ── Tests ────────────────────────────────────────────────────────────────────

def test_csv_presence():
    assert os.path.exists('pallet_positions.csv'), "Fichier CSV manquant !"


def test_load_positions_format():
    from main import LoadPalletPosition
    positions = LoadPalletPosition()
    assert len(positions) > 0, "Aucune position dans le CSV"
    assert len(positions[0]) == 6, f"Attendu 6 valeurs, obtenu {len(positions[0])}"


def test_robot_and_scene(robot):
    pos = robot.ReadPosition()
    assert len(pos) == 6, f"ReadPosition() doit retourner 6 valeurs, obtenu {len(pos)}"


def test_gripper_init(robot):
    assert robot.gripper is not None, "Le gripper n'a pas été attaché"