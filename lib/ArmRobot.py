import sys
import os
sys.path.append(os.getcwd())

from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math
import time
import numpy as np

class UniversalRobot:
    def __init__(self, robot_name, sim=None):
        # Injection de dépendance : on réutilise sim si fourni
        if sim:
            self.sim = sim
            self.simIK = self.sim.require('simIK')
        else:
            self.client = RemoteAPIClient()
            self.sim = self.client.require('sim')
            self.simIK = self.client.require('simIK')
            
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
        self.jointAccel = [40 * math.pi / 180] * 6
        self.jointJerk  = [80 * math.pi / 180] * 6
        self.gripper = None

    # ... (gardez le reste de vos méthodes MoveL, MoveJ, etc. inchangé)

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