import sys
import os
sys.path.append(os.getcwd())

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math
import time
from lib.interpolation import linear_interpolation
from lib.homogeneous_transform import *
import numpy as np


class UniversalRobot:
    def __init__(self, robot_name):
        client = RemoteAPIClient()
        self.sim = client.require('sim')
        self.simIK = client.require('simIK')
        self.robotName = robot_name

        self.simRobot  = self.sim.getObject(f'/{robot_name}')
        self.simTip    = self.sim.getObject(f'/{robot_name}/ikTip')
        self.simTarget = self.sim.getObject(f'/{robot_name}/ikTarget')

        self.simJoints = []
        for i in range(6):
            self.simJoints.append(self.sim.getObject(f'/{robot_name}/joint{i + 1}'))

        self.ikEnv   = self.simIK.createEnvironment()
        self.ikGroup = self.simIK.createGroup(self.ikEnv)
        self.simIK.addElementFromScene(
            self.ikEnv, self.ikGroup,
            self.simRobot, self.simTip, self.simTarget,
            self.simIK.constraint_pose
        )

        self.ikMaxVel  = 0.2
        self.ikMaxAccel = 0.1
        self.ikMaxJerk  = 0.1

        self.jointVel   = [180] * 6
        self.jointAccel = [40  * math.pi / 180] * 6
        self.jointJerk  = [80  * math.pi / 180] * 6

        self.gripper = None

    def GetObjectPosition(self, objectName):
        handle = self.sim.getObject(f'/{objectName}')
        pos = self.sim.getObjectPosition(handle, self.simRobot)
        ori = self.sim.getObjectOrientation(handle, self.simRobot)
        pos = [p * 1000 for p in pos]
        ori = [o * 180 / math.pi for o in ori]
        return pos + ori

    def GetObjectPosition2(self, objectHandle):
        pos = self.sim.getObjectPosition(objectHandle, self.simRobot)
        ori = self.sim.getObjectOrientation(objectHandle, self.simRobot)
        pos = [p * 1000 for p in pos]
        ori = [o * 180 / math.pi for o in ori]
        return pos + ori

    def ReadPosition(self):
        pos = self.sim.getObjectPosition(self.simTip, self.simRobot)
        ori = self.sim.getObjectOrientation(self.simTip, self.simRobot)
        pos = [p * 1000 for p in pos]
        ori = [o * 180 / math.pi for o in ori]
        return pos + ori

    def ReadJointPosition(self):
        return [self.sim.getJointPosition(j) * 180 / math.pi for j in self.simJoints]

    def SetSpeed(self, speed):
        self.ikMaxVel   = [speed / 1000] * 3 + [360 * math.pi / 180]
        self.ikMaxAccel = [speed * 2 / 1000] * 3 + [720 * math.pi / 180]
        self.ikMaxJerk  = [speed * 2 / 1000] * 3 + [720 * math.pi / 180]

    def ikCallback(self, target_quaternion, a, b):
        self.sim.setObjectPose(self.simTarget, -1, target_quaternion)
        self.simIK.applyIkEnvironmentToScene(self.ikEnv, self.ikGroup)

    def MoveL(self, targetPos, speed):
        self.SetSpeed(speed)
        pos = [targetPos[i] / 1000 for i in range(3)]
        ori = [targetPos[i + 3] * 3.14 / 180 for i in range(3)]
        self.sim.setObjectPosition(self.simTarget, self.simRobot, pos)
        self.sim.setObjectOrientation(self.simTarget, self.simRobot, ori)
        target_quaternion  = self.sim.getObjectPose(self.simTarget, -1)
        current_quaternion = self.sim.getObjectPose(self.simTip, -1)
        self.sim.moveToPose(
            -1, current_quaternion,
            self.ikMaxVel, self.ikMaxAccel, self.ikMaxJerk,
            target_quaternion, self.ikCallback, None, None
        )

    def SetJointSpeed(self, speed):
        self.jointVel = [speed * math.pi / 180] * 6

    def fkCallback(self, target_joint_pos, a, b, c):
        for i in range(6):
            self.sim.setJointTargetPosition(self.simJoints[i], target_joint_pos[i])

    def MoveJ(self, targetJointPos, speed):
        self.SetJointSpeed(speed)
        _targetJointPos = [j * math.pi / 180 for j in targetJointPos]
        param = {
            'joints':   self.simJoints,
            'targetPos': _targetJointPos,
            'maxVel':   self.jointVel,
            'maxAccel': self.jointAccel,
            'maxJerk':  self.jointJerk,
        }
        self.sim.moveToConfig(param)

    def AttachGripper(self, gripper_name):
        self.gripper = Gripper(self.sim, f'/{self.robotName}/{gripper_name}')


class Gripper:
    def __init__(self, sim, gripper_script_name):
        self.sim = sim
        self.gripper_script = self.sim.getScript(
            self.sim.scripttype_childscript, gripper_script_name
        )

    def Catch(self):
        self.sim.callScriptFunction('set_gripper', self.gripper_script, True)

    def Release(self):
        self.sim.callScriptFunction('set_gripper', self.gripper_script, False)