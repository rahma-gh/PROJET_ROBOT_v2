import math
import time
import numpy as np

from pyrep import PyRep
from pyrep.robots.arms.arm import Arm
from pyrep.robots.end_effectors.suction_cup import SuctionCup
from pyrep.objects.object import Object
from pyrep.objects.joint import Joint
from lib.interpolation import linear_interpolation
from lib.homogeneous_transform import *


# UR10 — hérite de la classe Arm de PyRep
class UR10Arm(Arm):
    def __init__(self, count: int = 0):
        super().__init__(count, 'UR10', num_joints=6)


# Classe principale du robot
class UniversalRobot:
    def __init__(self, robot_name: str, pr: PyRep):
        """
        robot_name : nom du robot dans la scène CoppeliaSim (ex: 'UR10')
        pr         : instance PyRep déjà lancée (pr.launch + pr.start)
        """
        self.pr = pr
        self.robot_name = robot_name
        self.arm = UR10Arm()
        self.gripper = None

    # Lire la position cartésienne du tip (mm + degrés)
    def ReadPosition(self):
        tip = self.arm.get_tip()
        pos = tip.get_position()                    # mètres
        ori = tip.get_orientation()                 # radians
        pos_mm  = [p * 1000 for p in pos]
        ori_deg = [o * 180 / math.pi for o in ori]
        return pos_mm + ori_deg

    # Lire la position des joints (degrés)
    def ReadJointPosition(self):
        joints_rad = self.arm.get_joint_positions()
        return [j * 180 / math.pi for j in joints_rad]

    # Obtenir la position d'un objet de la scène par son nom
    def GetObjectPosition(self, object_name: str):
        obj = Object.get_object(object_name)
        robot_base = Object.get_object(self.robot_name)
        pos = obj.get_position(relative_to=robot_base)
        ori = obj.get_orientation(relative_to=robot_base)
        pos_mm  = [p * 1000 for p in pos]
        ori_deg = [o * 180 / math.pi for o in ori]
        return pos_mm + ori_deg

    def GetObjectPosition2(self, object_handle):
        obj = Object(object_handle)
        robot_base = Object.get_object(self.robot_name)
        pos = obj.get_position(relative_to=robot_base)
        ori = obj.get_orientation(relative_to=robot_base)
        pos_mm  = [p * 1000 for p in pos]
        ori_deg = [o * 180 / math.pi for o in ori]
        return pos_mm + ori_deg

    # Déplacer le robot en mode linéaire (mm, degrés)
    def MoveL(self, target_pos, speed):
        current_pos = self.ReadPosition()
        interpolated_points, steps, time_per_step = linear_interpolation(
            current_pos, target_pos, speed, speed / 15
        )
        for point in interpolated_points:
            pos_m = [point[i] / 1000 for i in range(3)]
            ori_r = [point[i + 3] * math.pi / 180 for i in range(3)]
            tip = self.arm.get_tip()
            tip.set_position(pos_m)
            tip.set_orientation(ori_r)
            self.arm.solve_ik_via_jacobian(pos_m, ori_r)
            self.pr.step()
            t = max(time_per_step, 0.05)
            time.sleep(t)

    # Déplacer le robot en mode joint (degrés)
    def MoveJ(self, target_joint_pos, speed):
        target_rad = [j * math.pi / 180 for j in target_joint_pos]
        self.arm.set_joint_target_positions(target_rad)
        # Attendre que le mouvement se termine
        steps = int(abs(speed) / 10) + 10
        for _ in range(steps):
            self.pr.step()

    # Attacher le gripper
    def AttachGripper(self, gripper_name: str):
        self.gripper = VacuumGripper(gripper_name, self.pr)


# Gripper de type ventouse
class VacuumGripper:
    def __init__(self, gripper_name: str, pr: PyRep):
        self.pr = pr
        self.suction = SuctionCup(gripper_name)

    def Catch(self):
        self.suction.grasp(None)   # active la ventouse
        self.pr.step()

    def Release(self):
        self.suction.release()
        self.pr.step()