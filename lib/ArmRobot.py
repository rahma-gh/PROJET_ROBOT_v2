import sys
import os
import math
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

class UniversalRobot:
    def __init__(self, robot_name, sim=None):
        # Si sim est fourni (par pytest), on l'utilise.
        if sim is not None:
            self.sim = sim
        else:
            # Sinon on crée une nouvelle connexion
            self.client = RemoteAPIClient(host='localhost', port=23000)
            self.sim = self.client.require('sim')
            
        self.simIK = self.sim.require('simIK')
        self.robotName = robot_name

        # Handles
        self.simRobot  = self.sim.getObject(f'/{robot_name}')
        self.simTip    = self.sim.getObject(f'/{robot_name}/ikTip')
        self.simTarget = self.sim.getObject(f'/{robot_name}/ikTarget')

        self.simJoints = []
        for i in range(6):
            self.simJoints.append(self.sim.getObject(f'/{robot_name}/joint{i + 1}'))

        # Configuration IK
        self.ikEnv   = self.simIK.createEnvironment()
        self.ikGroup = self.simIK.createGroup(self.ikEnv)
        self.simIK.addElementFromScene(self.ikEnv, self.ikGroup, self.simRobot, 
                                       self.simTip, self.simTarget, self.simIK.constraint_pose)

    def ReadPosition(self):
        pos = self.sim.getObjectPosition(self.simTip, self.simRobot)
        ori = self.sim.getObjectOrientation(self.simTip, self.simRobot)
        return [p * 1000 for p in pos] + [o * 180 / math.pi for o in ori]

    def MoveL(self, targetPos, speed):
        # Logique simplifiée pour le test
        pos = [targetPos[i] / 1000 for i in range(3)]
        self.sim.setObjectPosition(self.simTarget, self.simRobot, pos)
        self.simIK.applyIkEnvironmentToScene(self.ikEnv, self.ikGroup)

    def AttachGripper(self, gripper_name):
        self.gripper = Gripper(self.sim, f'/{self.robotName}/{gripper_name}')

class Gripper:
    def __init__(self, sim, gripper_script_name):
        self.sim = sim
        self.gripper_script = self.sim.getScript(self.sim.scripttype_childscript, gripper_script_name)

    def Catch(self):
        self.sim.callScriptFunction('set_gripper', self.gripper_script, True)

    def Release(self):
        self.sim.callScriptFunction('set_gripper', self.gripper_script, False)