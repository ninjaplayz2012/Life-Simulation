from Entities import ImageEntity, Shader, BaseVector
from Window import Window
import numpy as np
import json

GremlinVertices = [
	BaseVector(Position=[0.0, 100, 0.0], TexCoord = [0.0, 1.0]),
	BaseVector(Position=[0.0, 0.0, 0.0], TexCoord = [0.0, 0.0]),
	BaseVector(Position=[100, 0.0, 0.0], TexCoord = [1.0, 0.0]),
	BaseVector(Position=[100, 100, 0.0], TexCoord = [1.0, 1.0])
]
GremlinIndices = [
    0, 1, 2,
    0, 2, 3
]

def ClampToRadius(Point, Center, Radius):
    Offset = Point - Center
    Distance = np.linalg.norm(Offset)
    
    if Distance > Radius:
        Point = Center + (Offset / Distance) * Radius
    
    return Point

def GetRandomColor():
    R, G, B = np.random.random(3)
    return [R, G, B, 1]

with open("./Resources/Names.json", "r") as file:
    Data = json.load(file)

Names = Data['Names']
class Gremlin:
    def __init__(self, Shader: Shader, Window: Window, Position=None):
        self.Entity = ImageEntity(["./Resources/Gremlin.png", "./Resources/DeadGremlin.png"], Shader, GremlinVertices, GremlinIndices)
        self.Entity.PositionScale = Position if Position is not None else np.random.random(2)
        self.Entity.Color = np.clip(GetRandomColor(), 0.5, 1)
        self.Entity.GetSize(Window)
        self.Entity.SetDefaultUniforms()
        self.Entity.Generate()
        Window.World.AddEntity(self.Entity)
        
        self.WalkSpeed = np.linalg.norm(np.array([10, 10]) / np.array(Window.Size))
        self.TargetedBush: Bush = None
        self.CurrentTime = 0
        self.Busy = False
        self.BusyDuration = 0
        self.WalkDirection = np.array([0, 0])
        self.IdlePosition = self.Entity.PositionScale
        self.IdleRadius = np.linalg.norm(np.array([50, 50]) / np.array(Window.Size))
        self.Hunger = 100
        self.Name = Names.pop(np.random.choice(len(Names)))
        
        self.MatePosition = np.array([0.5, 0.5])
        self.MateCooldown = 5
        self.Mate: Gremlin = None
        print(f"{self.Name} Spawned at {self.Position}")
    
    def TargetBush(self, Bush: Bush):
        Bush.Targeted = True
        self.TargetedBush = Bush
        self.CurrentTime = 0
        self.Busy = True
        
        Distance = np.linalg.norm(Bush.Position - self.Position)
        self.BusyDuration = max(Distance / self.WalkSpeed, 1e-3)
    
    def MakeBabyGremlin(self, Window: Window):
        return Gremlin(self.Entity._Shader, Window, self.MatePosition)
    
    def Walk(self, DeltaTime, Window):
        if self.Busy and self.Mate and self.Hunger > 20:
            return self.WalkToMate(DeltaTime, Window)
        elif self.Busy and self.Mate:
            self.Mate.Mate = None
            self.Mate.Busy = False
            self.Mate = None
            self.Busy = False
        
        if self.Busy:
            self.WalkToBush(DeltaTime)
        else:
            self.CurrentTime += DeltaTime
            if self.CurrentTime >= 2.5:
                self.WalkDirection = np.random.random(2) / 10
                self.CurrentTime = 0
            self.Position = ClampToRadius(self.Position + self.WalkDirection * DeltaTime, self.IdlePosition, self.IdleRadius)
    
    def WalkToBush(self, DeltaTime):
        self.CurrentTime += DeltaTime
        Time = np.clip([self.CurrentTime / self.BusyDuration], 0, 1)[0]
        self.Position = self.Position + (self.TargetedBush.Position - self.Position) * Time
        Distance = np.linalg.norm(self.TargetedBush.Position - self.Position)
        if Distance <= 1e-3:
            self.Eat()
            self.Busy = False
            self.IdlePosition = self.Position
            self.CurrentTime = 0
    
    def WalkToMate(self, DeltaTime, Window):
        self.CurrentTime += DeltaTime
        
        Distance = np.linalg.norm(self.MatePosition - self.Position)
        MateDistance = np.linalg.norm(self.MatePosition - self.Mate.Position)
        self.BusyDuration = max(Distance / self.WalkSpeed, 1e-3)
        
        if Distance <= 1e-3 and MateDistance <= 1e-3:
            Baby = self.MakeBabyGremlin(Window)
            print(f"{self.Name} Mated with {self.Mate.Name} to make {Baby.Name} at {self.MatePosition}")
            self.Busy = False
            self.Hunger -= 25
            self.Mate.Hunger -= 25
            self.Mate.MateCooldown = 10
            self.Mate.IdlePosition = self.Mate.Position
            self.Mate.Mate = None
            self.Mate.Busy = False
            self.Mate = None
            self.IdlePosition = self.Position
            self.MateCooldown = 10
            return Baby
        elif Distance > 1e-3:
            Time = np.clip([self.CurrentTime / self.BusyDuration], 0, 1)[0]
            self.Position = self.Position + (self.MatePosition - self.Position) * Time
    
    def Eat(self):
        self.Hunger += 50
        self.TargetedBush.Eat()
        self.TargetedBush = None
    
    def Kill(self):
        self.Entity.CurrentTexture = 1
    
    def Delete(self, Window: Window):
        Window.World.RemoveEntity(self.Entity)
        self.Entity.Delete()
        del self
    
    def __str__(self):
        return f"Name: {self.Name}, Hunger: {self.Hunger}, Mate Cooldown: {self.MateCooldown}, Busy: {self.Busy}"
    
    @property
    def Position(self):
        return self.Entity.PositionScale
    @Position.setter
    def Position(self, Value):
        self.Entity.PositionScale = Value

class Bush:
    def __init__(self, Shader: Shader, Window: Window):
        self.Entity = ImageEntity(["./Resources/Bush.png", "./Resources/Bush2.png"], Shader, GremlinVertices, GremlinIndices)
        self.Entity.PositionScale = np.random.random(2)
        self.Entity.Scale = 0.75
        self.Entity.GetSize(Window)
        self.Entity.SetDefaultUniforms()
        self.Entity.Generate()
        Window.World.AddEntity(self.Entity)
        
        self.Targeted = False
        self.Regrowing = False
        self.DownTime = 0
    
    def Eat(self):
        self.Entity.CurrentTexture = 1
        self.Targeted = False
        self.Regrowing = True
        self.DownTime = 0
    
    def Regrow(self):
        self.Entity.CurrentTexture = 0
        self.DownTime = 0
        self.Regrowing = False
    
    @property
    def Position(self):
        return self.Entity.PositionScale
    @Position.setter
    def Position(self, Value):
        self.Entity.PositionScale = Value