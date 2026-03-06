import os
import sys
import csv
import time
sys.path.append(os.getcwd())

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
from lib.ArmRobot import UniversalRobot, Gripper

# Initialize CoppeliaSim Remote API Client
client = RemoteAPIClient()
sim = client.require('sim')

# Initialize the UR10 robot and attach the vacuum gripper
armRobot = UniversalRobot('UR10')
armRobot.AttachGripper('vacuum_gripper')


def SavePalletPosition():
    with open('pallet_positions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        height = 0
        for i in range(21):
            if i != 0 and i % 7 == 0:
                height = height + 200
            pos = armRobot.GetObjectPosition(f'Cartoons{i + 1}')
            print(pos)
            writer.writerow(pos)
            time.sleep(0.2)


def LoadPalletPosition():
    positions = []
    with open('pallet_positions.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            positions.append([float(i) for i in row])
    return positions


def putObjectToPallet(count, palletPos):
    pos = [570, 0, palletPos[2] + 400, 180, 0, palletPos[5] - 90]
    if count > 13:
        pos = [570, 0, palletPos[2] + 100, 180, 0, palletPos[5] - 90]
    armRobot.MoveL(pos, 300)

    target_pos_up   = [palletPos[0], palletPos[1], palletPos[2] + 200,       180, 0, palletPos[5] - 90]
    target_pos_down = [palletPos[0], palletPos[1], palletPos[2] + 110,       180, 0, palletPos[5] - 90]

    if count > 13:
        target_pos_up   = [palletPos[0], palletPos[1], palletPos[2] + 150 - 200, 180, 0, palletPos[5] - 90]
        target_pos_down = [palletPos[0], palletPos[1], palletPos[2] + 110 - 200, 180, 0, palletPos[5] - 90]

    armRobot.MoveL(target_pos_up, 500)
    jointPos = armRobot.ReadJointPosition()
    print(f'Joint position [{count}]: {jointPos}')
    armRobot.MoveL(target_pos_down, 50)
    armRobot.gripper.Release()
    armRobot.MoveL(target_pos_up, 500)

    standby_joints = [-14.211824351788398, 23.613074715029327, 122.55519954862501,
                      -56.18447177751439, -90.09695623063273, 75.74877825490448]
    armRobot.MoveJ(standby_joints, 180)


def main():
    sim.startSimulation()

    prox_sensor = sim.getObject('/ConveyorSensor')
    targetPositions = LoadPalletPosition()

    standbyPos = [570, 0, 400, 180, 0, 90]
    armRobot.MoveL(standbyPos, 100)

    count = 0
    while count < 21:
        ret, dist, pos, handle, norm = sim.readProximitySensor(prox_sensor)
        if ret == 1:
            print('New object detected...')
            time.sleep(0.2)
            box_position = armRobot.GetObjectPosition2(handle)
            pickUpPos = [box_position[0], box_position[1], box_position[2] + 105, 180, 0, 90]
            armRobot.MoveL(pickUpPos, 300)
            armRobot.gripper.Catch()
            putObjectToPallet(count, targetPositions[count])
            count += 1
            print(f'Object {count} placed.\n')
        time.sleep(0.1)

    time.sleep(5)
    sim.stopSimulation()


if __name__ == '__main__':
    main()