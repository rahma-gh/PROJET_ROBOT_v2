import os
import sys
import csv
import time
sys.path.append(os.getcwd())

from pyrep import PyRep
from lib.ArmRobot import UniversalRobot

SCENE_FILE = os.path.join(os.path.dirname(__file__), 'pick_and_place.ttt')


def get_pr_and_robot(headless=True):
    """Initialise PyRep et le robot. Retourne (pr, robot)."""
    pr = PyRep()
    pr.launch(SCENE_FILE, headless=headless)
    pr.start()
    robot = UniversalRobot('UR10', pr)
    robot.AttachGripper('vacuum_gripper')
    return pr, robot


# Enregistrer les positions de la palette
def SavePalletPosition(pr, robot):
    with open('pallet_positions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for i in range(21):
            pos = robot.GetObjectPosition(f'Cartoons{i + 1}')
            print(pos)
            writer.writerow(pos)
            pr.step()


# Charger les positions depuis le CSV
def LoadPalletPosition():
    positions = []
    with open('pallet_positions.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            positions.append([float(v) for v in row])
    return positions


# Déposer un objet sur la palette
def putObjectToPallet(pr, robot, count, palletPos):
    pos = [570, 0, palletPos[2] + 400, 180, 0, palletPos[5] - 90]
    if count > 13:
        pos = [570, 0, palletPos[2] + 100, 180, 0, palletPos[5] - 90]
    robot.MoveL(pos, 300)

    target_pos_up   = [palletPos[0], palletPos[1], palletPos[2] + 200,       180, 0, palletPos[5] - 90]
    target_pos_down = [palletPos[0], palletPos[1], palletPos[2] + 110,       180, 0, palletPos[5] - 90]

    if count > 13:
        target_pos_up   = [palletPos[0], palletPos[1], palletPos[2] + 150 - 200, 180, 0, palletPos[5] - 90]
        target_pos_down = [palletPos[0], palletPos[1], palletPos[2] + 110 - 200, 180, 0, palletPos[5] - 90]

    robot.MoveL(target_pos_up, 500)
    robot.MoveL(target_pos_down, 50)
    robot.gripper.Release()
    robot.MoveL(target_pos_up, 500)

    standby_joints = [-14.21, 23.61, 122.55, -56.18, -90.10, 75.75]
    robot.MoveJ(standby_joints, 180)


def main():
    pr, robot = get_pr_and_robot(headless=True)

    try:
        targetPositions = LoadPalletPosition()
        standbyPos = [570, 0, 400, 180, 0, 90]
        robot.MoveL(standbyPos, 100)

        count = 0
        while count < 21:
            pr.step()
            # La détection du capteur se fait via PyRep directement
            # (à adapter selon le nom du capteur dans la scène)
            time.sleep(0.1)
    finally:
        pr.stop()
        pr.shutdown()


if __name__ == '__main__':
    main()