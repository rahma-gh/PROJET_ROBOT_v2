import sys
import os
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math

class UniversalRobot:
    def __init__(self, robot_name, sim=None):
        # Si sim est fourni (par pytest), on l'utilise. 
        # Sinon on crée une nouvelle connexion (pour main.py)
        if sim is not None:
            self.sim = sim
        else:
            self.client = RemoteAPIClient()
            self.sim = self.client.require('sim')
            
        self.simIK = self.sim.require('simIK')
        self.robotName = robot_name

        self.simRobot  = self.sim.getObject(f'/{robot_name}')
        self.simTip    = self.sim.getObject(f'/{robot_name}/ikTip')
        self.simTarget = self.sim.getObject(f'/{robot_name}/ikTarget')

        self.simJoints = []
        for i in range(6):
            self.simJoints.append(self.sim.getObject(f'/{robot_name}/joint{i + 1}'))

        self.ikEnv   = self.simIK.createEnvironment()
        self.ikGroup = self.simIK.createGroup(self.ikEnv)
        self.simIK.addElementFromScene(self.ikEnv, self.ikGroup, self.simRobot, 
                                       self.simTip, self.simTarget, self.simIK.constraint_pose)

    def ReadPosition(self):
        pos = self.sim.getObjectPosition(self.simTip, self.simRobot)
        ori = self.sim.getObjectOrientation(self.simTip, self.simRobot)
        return [p * 1000 for p in pos] + [o * 180 / math.pi for o in ori]

    def AttachGripper(self, gripper_name):
        from lib.ArmRobot import Gripper # Import local pour éviter les cycles
        self.gripper = Gripper(self.sim, f'/{self.robotName}/{gripper_name}')

class Gripper:
    def __init__(self, sim, gripper_script_name):
        self.sim = sim
        self.gripper_script = self.sim.getScript(self.sim.scripttype_childscript, gripper_script_name)

    def Catch(self):
        self.sim.callScriptFunction('set_gripper', self.gripper_script, True)

    def Release(self):
        self.sim.callScriptFunction('set_gripper', self.gripper_script, False)