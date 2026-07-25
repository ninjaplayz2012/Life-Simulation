import glfw
from Shaders import Shader
from Window import Window, World
from Entities import *
from OpenGL.GL import *

Vertices = [
    BaseVector([-0.5,  0.5, 0.0], Color = [1.0, 0.0, 0.0, 1.0]), #TexCoord = [0.0, 1.0]),  # Top-Left
    BaseVector([-0.5, -0.5, 0.0], Color = [0.0, 1.0, 0.0, 1.0]), #TexCoord = [0.0, 0.0]),  # Bottom-Left
    BaseVector([ 0.5, -0.5, 0.0], Color = [0.0, 0.0, 1.0, 1.0]), #TexCoord = [1.0, 0.0]),  # Bottom-Right
    BaseVector([ 0.5,  0.5, 0.0], Color = [1.0, 1.0, 0.0, 1.0])  #TexCoord = [1.0, 1.0])  # Top-Right
]

TextureVertices = [
    BaseVector([-0.5,  0.5, 0.0], TexCoord = [0.0, 1.0]),  # Top-Left
    BaseVector([-0.5, -0.5, 0.0], TexCoord = [0.0, 0.0]),  # Bottom-Left
    BaseVector([ 0.5, -0.5, 0.0], TexCoord = [1.0, 0.0]),  # Bottom-Right
    BaseVector([ 0.5,  0.5, 0.0], TexCoord = [1.0, 1.0])  # Top-Right
]

Indices = [
    0, 1, 2,
    0, 2, 3
]

if not glfw.init():
    raise RuntimeError("Failed to initialize GLFW.")

WorldObject = World()
OpenGLWindow = Window(WorldObject, [500, 500])

OpenGLWindow.Display()

TextureShaderObject = Shader("./Shaders/TextureVertexShader.vert", "./Shaders/TextureFragmentShader.frag")
TextureShaderObject.Compile()

ShaderObject = Shader("./Shaders/DefaultVertexShader.vert", "./Shaders/DefaultFragmentShader.frag")
ShaderObject.Compile()

TextureEntity = ImageEntity(["./Resources/Untitled.png"], TextureShaderObject, TextureVertices, Indices)
TextureEntity.Scale = 1
TextureEntity.Generate()

Entity = BaseEntity(ShaderObject, Vertices, Indices)
Entity.Scale = 1.5
Entity.Generate()

WorldObject.AddEntity(Entity)
WorldObject.AddEntity(TextureEntity)
OpenGLWindow.SetBackgroundColor(1, 1, 1, 1)

def EntityChanges(DeltaTime):
    # Time = glfw.get_time()
    # Position = np.array([np.cos(Time) / 1.5, np.sin(Time) / 1.5, 0])
    # Entity.Position = Position
    # TextureEntity.Position = -Position
    TextureEntity.Rotation -= DeltaTime
    pass

if __name__ == '__main__':
    OpenGLWindow.StartRenderLoop(EntityChanges)

glfw.terminate()