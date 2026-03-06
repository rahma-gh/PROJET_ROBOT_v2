import os
import sys
import csv
import time
sys.path.append(os.getcwd())

def LoadPalletPosition():
    positions = []
    if not os.path.exists('pallet_positions.csv'):
        return []
    with open('pallet_positions.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            positions.append([float(i) for i in row])
    return positions

def _get_sim():
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient
    client = RemoteAPIClient()
    return client.require('sim')

def SavePalletPosition():
    from lib.ArmRobot import UniversalRobot
    sim = _get_sim()
    # On passe sim ici
    armRobot = UniversalRobot('UR10', sim=sim)
    armRobot.AttachGripper('vacuum_gripper')
    with open('pallet_positions.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for i in range(21):
            pos = armRobot.GetObjectPosition(f'Cartoons{i + 1}')
            writer.writerow(pos)
            time.sleep(0.1)

def putObjectToPallet(armRobot, count, palletPos):
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
    armRobot.MoveL(target_pos_down, 50)
    armRobot.gripper.Release()
    armRobot.MoveL(target_pos_up, 500)

    standby_joints = [-14.211824351788398, 23.613074715029327, 122.55519954862501,
                      -56.18447177751439, -90.09695623063273, 75.74877825490448]
    armRobot.MoveJ(standby_joints, 180)

def main():
    from lib.ArmRobot import UniversalRobot
    sim = _get_sim()
    armRobot = UniversalRobot('UR10', sim=sim)
    armRobot.AttachGripper('vacuum_gripper')

    sim.startSimulation()
    prox_sensor = sim.getObject('/ConveyorSensor')
    targetPositions = LoadPalletPosition()

    armRobot.MoveL([570, 0, 400, 180, 0, 90], 100)

    count = 0
    while count < len(targetPositions):
        ret, dist, pos, handle, norm = sim.readProximitySensor(prox_sensor)
        if ret == 1:
            time.sleep(0.2)
            box_position = armRobot.GetObjectPosition2(handle)
            armRobot.MoveL([box_position[0], box_position[1], box_position[2] + 105, 180, 0, 90], 300)
            armRobot.gripper.Catch()
            putObjectToPallet(armRobot, count, targetPositions[count])
            count += 1
        time.sleep(0.05)

    sim.stopSimulation()

if __name__ == '__main__':
    main()