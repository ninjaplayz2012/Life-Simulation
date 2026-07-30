from __future__ import annotations
import numpy as np


class BaseVector:
    def __init__(self, Position = None, PositionScale = None, TexCoord=None, Color=None, InstanceBasedData=None):
        self.Position = np.array(Position, dtype=np.float32) if Position is not None else np.array([0, 0, 0], dtype=np.float32)
        self.PositionScale = np.array(PositionScale, dtype=np.float32) if PositionScale is not None else np.array([0, 0], dtype=np.float32)
        self.TexCoord = np.array(TexCoord, dtype=np.float32) if TexCoord is not None else None
        self.Color = np.array(Color, dtype=np.float32) if Color is not None else [1, 1, 1, 1]
        self.InstanceBasedData = np.array(InstanceBasedData, dtype=np.float32) if InstanceBasedData is not None else None

    def Unpack(self):
        Parts = [self.Position, self.PositionScale]
        
        if self.TexCoord is not None:
            Parts.append(self.TexCoord)
        if self.Color is not None:
            Parts.append(self.Color)
        
        return np.concatenate(Parts).astype(np.float32)

    def __repr__(self):
        return f"BaseVector(Position={self.Position}, TexCoord={self.TexCoord}, Color={self.Color})"

    def __add__(self, Vector: "BaseVector"):
        return BaseVector(self.Position + Vector.Position, self.TexCoord, self.Color)

    def __sub__(self, Vector: "BaseVector"):
        return BaseVector(self.Position - Vector.Position, self.TexCoord, self.Color)

    def __mul__(self, Other):
        if isinstance(Other, BaseVector):
            return self.Position @ Other.Position
        return BaseVector(self.Position * Other, self.TexCoord, self.Color)

    def __rmul__(self, Scalar):
        return BaseVector(self.Position * Scalar, self.TexCoord, self.Color)

    def __truediv__(self, Other):
        if isinstance(Other, BaseVector):
            return BaseVector(self.Position / Other.Position, self.TexCoord, self.Color)
        return BaseVector(self.Position / Other, self.TexCoord, self.Color)

    def __floordiv__(self, Other):
        if isinstance(Other, BaseVector):
            return BaseVector(self.Position // Other.Position, self.TexCoord, self.Color)
        return BaseVector(self.Position // Other, self.TexCoord, self.Color)

    def __mod__(self, Other):
        if isinstance(Other, BaseVector):
            return BaseVector(self.Position % Other.Position, self.TexCoord, self.Color)
        return BaseVector(self.Position % Other, self.TexCoord, self.Color)

    def __divmod__(self, Other):
        if isinstance(Other, BaseVector):
            return (self.Position // Other.Position, self.Position % Other.Position)
        return (self.Position // Other, self.Position % Other)
    
    def __iadd__(self, Vector: "BaseVector"):
        self.Position += Vector.Position
        return self

    def __isub__(self, Vector: "BaseVector"):
        self.Position -= Vector.Position
        return self

    def __imul__(self, Other):
        if isinstance(Other, BaseVector):
            self.Position = self.Position @ Other.Position
        else:
            self.Position *= Other
        return self

    def __itruediv__(self, Other):
        if isinstance(Other, BaseVector):
            self.Position /= Other.Position
        else:
            self.Position /= Other
        return self

    def __ifloordiv__(self, Other):
        if isinstance(Other, BaseVector):
            self.Position //= Other.Position
        else:
            self.Position //= Other
        return self

    def __imod__(self, Vector: "BaseVector"):
        self.Position %= Vector.Position
        return self