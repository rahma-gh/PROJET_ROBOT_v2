import sys
import os
import math
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class UniversalRobot:
    def __init__(self, robot_name, sim=None):
        if sim is not None:
            self.sim = sim
            # Pour simIK on crée une connexion séparée
            _client = RemoteAPIClient(host='localhost', port=23000)
            self.simIK = _client.require('simIK')
        else:
            _client = RemoteAPIClient(host='localhost', port=23000)
            self.sim = _client.require('sim')
            self.simIK = _client.require('simIK')

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

        self.gripper = None

    def ReadPosition(self):
        pos = self.sim.getObjectPosition(self.simTip, self.simRobot)
        ori = self.sim.getObjectOrientation(self.simTip, self.simRobot)
        return [p * 1000 for p in pos] + [o * 180 / math.pi for o in ori]

    def GetObjectPosition(self, objectName):
        handle = self.sim.getObject(f'/{objectName}')
        pos = self.sim.getObjectPosition(handle, self.simRobot)
        ori = self.sim.getObjectOrientation(handle, self.simRobot)
        return [p * 1000 for p in pos] + [o * 180 / math.pi for o in ori]

    def GetObjectPosition2(self, objectHandle):
        pos = self.sim.getObjectPosition(objectHandle, self.simRobot)
        ori = self.sim.getObjectOrientation(objectHandle, self.simRobot)
        return [p * 1000 for p in pos] + [o * 180 / math.pi for o in ori]

    def MoveL(self, targetPos, speed):
        pos = [targetPos[i] / 1000 for i in range(3)]
        self.sim.setObjectPosition(self.simTarget, self.simRobot, pos)
        self.simIK.applyIkEnvironmentToScene(self.ikEnv, self.ikGroup)

    def MoveJ(self, targetJointPos, speed):
        import math
        for i, joint in enumerate(self.simJoints):
            self.sim.setJointTargetPosition(joint, targetJointPos[i] * math.pi / 180)

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