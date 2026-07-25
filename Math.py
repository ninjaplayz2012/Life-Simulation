import numpy as np

def Get2dRotationMatrix(Rotation: float) -> np.matrix[2, 2]:
    return np.matrix([[np.cos(Rotation), -np.sin(Rotation)], [np.sin(Rotation), np.cos(Rotation)]], np.float32)

def Get2dRotationMatrixDeg(RotationDeg: float) -> np.matrix[2, 2]:
    Rotation = np.deg2rad(RotationDeg)
    return np.matrix([[np.cos(Rotation), -np.sin(Rotation)], [np.sin(Rotation), np.cos(Rotation)]], np.float32)