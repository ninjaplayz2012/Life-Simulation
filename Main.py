#--{ Imports }--#
import glfw
from Shaders import Shader
from Window import Window, World
from WorldGenerator import WorldGenerator
from Entities import *
from OpenGL.GL import *
from math import cos, sqrt
from Gremlin import *
import numpy as np
import numpy.typing as npt

#--{ Variables }--#
Size = 100

GremlinVertices = [
	BaseVector(Position=[   0, Size, 0.0], TexCoord = [0.0, 1.0]),
	BaseVector(Position=[   0,    0, 0.0], TexCoord = [0.0, 0.0]),
	BaseVector(Position=[Size,    0, 0.0], TexCoord = [1.0, 0.0]),
	BaseVector(Position=[Size, Size, 0.0], TexCoord = [1.0, 1.0])
]

BushVertices = [
	BaseVector(Position=[   0, Size, 0.0], TexCoord = [0.0, 1.0]),
	BaseVector(Position=[   0,    0, 0.0], TexCoord = [0.0, 0.0]),
	BaseVector(Position=[Size,    0, 0.0], TexCoord = [1.0, 0.0]),
	BaseVector(Position=[Size, Size, 0.0], TexCoord = [1.0, 1.0])
]

Indices = [
	0, 1, 2,
	0, 2, 3
]

def GetRandomPositions(Amount):
	Positions = []
	
	for i in range(Amount):
		Positions.append(np.random.random(2))
	
	return Positions

def GetRandomColors(Amount):
	Colors = []
	
	for i in range(Amount):
		r, g, b = np.clip(np.random.random(3), 0.5, 1)
		Colors.append([r, g, b, 1])
	
	return Colors

#--{ Main Function }--#
def Main():
	#--[ GLFW Initialization ]--#
	if not glfw.init():
		raise RuntimeError("Failed to initialize GLFW.")

	#--[ Window & World Creation ]--#
	WorldObject = World()
	
	OpenGLWindow = Window(WorldObject, [500, 500])
	OpenGLWindow.Display()
	OpenGLWindow.SetBackgroundColorHex("#1e1e2eFF")
	
	#--[ Shaders ]--#
	ShaderObject = Shader("./Shaders/TextureVertexShader.vert", "./Shaders/TextureFragmentShader.frag")
	
	# This compiles and adds all necessary global uniforms
	Shaders = [ShaderObject]
	OpenGLWindow.Update(Shaders)
	
	#--[ Entities ]--#
	BushAmount = np.random.randint(1, 10)
	Bushes: list[Bush] = np.array([Bush(ShaderObject, OpenGLWindow) for i in range(BushAmount)])
	
	IsValid = np.vectorize(lambda Bush: not (Bush.Targeted or Bush.Regrowing))
	IsRegrowing = np.vectorize(lambda Bush: Bush.Regrowing)
	
	StartingGremlinCount = 3
	Gremlins: list[Gremlin] = np.array([Gremlin(ShaderObject, OpenGLWindow) for i in range(StartingGremlinCount)])
	CanMate = np.vectorize(lambda Gremlin: (not Gremlin.MateCooldown and Gremlin.Hunger >= 90 and Gremlin.Mate is None))
	
	#--[ Functions ]--#
	Frame = 0
	def EntityChanges(DeltaTime):
		nonlocal Gremlins
		nonlocal Frame
		
		RegrowingMask = IsRegrowing(Bushes)
		for Bush in Bushes[RegrowingMask]:
			Bush.DownTime += DeltaTime
			if Bush.DownTime >= 5:
				Bush.Regrow()
		
		DeadGremlins = []
		BabyGremlins = []
		for Gremlin in Gremlins:
			ValidBushMask = IsValid(Bushes)
			MateMask = CanMate(Gremlins)
			
			Gremlin.Hunger -= 1 / 10
			Gremlin.MateCooldown = np.clip([Gremlin.MateCooldown - DeltaTime], 0, 10)[0]
			if not Gremlin.Busy and len(Bushes[ValidBushMask]) and Gremlin.Hunger <= 50:
				Positions = np.array([Bush.Position for Bush in Bushes[ValidBushMask]])
				Closest = np.sum((Positions - Gremlin.Position) ** 2, axis=1).argmin()
				Gremlin.TargetBush(Bushes[ValidBushMask][Closest])
			elif CanMate(Gremlin) and len(Gremlins[MateMask]) >= 2:
				Candidates = Gremlins[MateMask]
				Candidates = Candidates[Candidates != Gremlin]
				
				if len(Candidates) >= 1:
					Positions = np.array([G.Position for G in Candidates])
					Closest = np.sum((Positions - Gremlin.Position) ** 2, axis=1).argmin()
					Gremlin.Mate = Candidates[Closest]
					Gremlin.Busy = True
					Gremlin.MatePosition = Gremlin.Position + (Gremlin.Mate.Position - Gremlin.Position) * 0.5
					Gremlin.Mate.Mate = Gremlin
					Gremlin.Mate.MatePosition = Gremlin.MatePosition
					Gremlin.Mate.Busy = True
			
			Baby = Gremlin.Walk(DeltaTime, OpenGLWindow)
			if not Baby: continue
			BabyGremlins.append(Baby)
		
		AliveMask = np.array([Gremlin.Hunger > 0 for Gremlin in Gremlins], dtype=bool)
		DeadGremlins = Gremlins[~AliveMask]

		for Gremlin in DeadGremlins:
			Gremlin.Kill()
		
		Gremlins = Gremlins[AliveMask]
		Gremlins = np.concatenate([Gremlins, np.array(BabyGremlins)])
		
		Frame += 1
	
	#--[ Rendering ]--#
	OpenGLWindow.StartRenderLoop(EntityChanges)
	
	#--[ Termination ]--#
	try:
		for ShaderObj in Shaders:
			ShaderObj.Delete()
			
		OpenGLWindow.Delete()
	except Exception:
		pass
	
	glfw.terminate()

if __name__ == '__main__':
	Main()