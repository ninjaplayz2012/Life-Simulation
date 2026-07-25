import glfw
from Vectors import BaseVector
from OpenGL.GL import *
from Events import Event
from Shaders import *
from Math import Get2dRotationMatrix

# Base object class for all objects
class BaseObject:
    def __init__(self):
        self.PropertyChanged = Event()

# Base Entity class (entites are objects that are rendered) this class holds the properties of all entities
class BaseEntity(BaseObject):
    def __init__(self, ObjectShader: Shader, Vertices: list[BaseVector] = None, Indices: list[int] | None = None):
        super().__init__()
        
        self.Vertices = Vertices if Vertices else []
        self.Indices = Indices
        self.Position = np.array([0, 0, 0], np.float32)
        self.Scale = 1.0
        
        self.VAO = VertexArrayObject()
        self.VBO = VertexBufferObject(np.concatenate([Vertex.Unpack() for Vertex in Vertices]))
        self.EBO = ElementArrayBufferObject(np.array(Indices, np.int32)) if Indices else None
        
        self._Rotation = 0
        self._RotationMatrix = Get2dRotationMatrix(0)
        self._Shader = ObjectShader
        self._Visible = True
        self._Uniforms: list[Uniform] = []
        self.SetUniform("Position", lambda Location, Data : glUniform3f(Location, *self.Position))
        self.SetUniform("Scale", lambda Location, Data : glUniform1f(Location, self.Scale))
        self.SetUniform("Rotation", lambda Location, Data : glUniformMatrix2fv(Location, 1, GL_FALSE, self._RotationMatrix))
    
    def SetUniform(self, Name: str, Setter, Data = None):
        UniformId = glGetUniformLocation(self._Shader.Shader, Name)
        self._Uniforms.append(Uniform(UniformId, Setter, Data))
    
    def Generate(self):
        self.VAO.Bind()
        self.VBO.Bind()
        if self.EBO:
            self.EBO.Bind()
        
        Stride = 7 * 4
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, Stride, 0)
        self.VAO.LinkAttrib(self.VBO, 1, 4, GL_FLOAT, Stride, 3 * 4)
        
        self.VAO.Unbind()
    
    def Render(self, DrawType):
        self._Shader.Activate()
        self.Bind()
        
        for Uniform in self._Uniforms:
            Uniform.Set()
        
        if self.EBO:
            glDrawElements(DrawType, len(self.Indices), GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(DrawType, 0, len(self.Vertices))
        
        self.Unbind()
        
    def Bind(self):
        self.VAO.Bind()
        self.VBO.Bind()
        
        if self.EBO:
            self.EBO.Bind()

    def Unbind(self):
        self.VAO.Unbind()
    
    @property
    def Visible(self):
        return self._Visible
    
    @Visible.setter
    def Visible(self, Value):
        if Value == self._Visible:
            return
        
        self._Visible = Value
        self.PropertyChanged.Fire("Visible", Value)

    @property
    def Rotation(self):
        return self._Rotation
    
    @Rotation.setter
    def Rotation(self, Value):
        if Value == self._Rotation:
            return
        
        self._Rotation = Value
        self._RotationMatrix = Get2dRotationMatrix(self.Rotation)
        self.PropertyChanged.Fire("Rotation", Value)

class ImageEntity(BaseEntity):
    def __init__(self, ImagePaths: list[str], ObjectShader: Shader, Vertices: list[BaseVector] = [], Indices: list[int] | None = None):
        super().__init__(ObjectShader, Vertices, Indices)
        
        if isinstance(ImagePaths, str):
            ImagePaths = [ImagePaths]
        
        self._Textures = [Texture(Path, Index) for Index, Path in enumerate(ImagePaths)]
        self.SetUniform("Tex0", lambda Location, Data : glUniform1i(Location, 0))
    
    def Generate(self):
        for Texture in self._Textures:
            Texture.Generate()
        
        Stride = 5 * 4
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, Stride, 0)
        self.VAO.LinkAttrib(self.VBO, 1, 2, GL_FLOAT, Stride, 12)
    
    def Render(self, DrawType):
        self._Shader.Activate()
        self.Bind()
        
        for Uniform in self._Uniforms:
            Uniform.Set()
        
        for Texture in self._Textures:
            Texture.Activate()
            Texture.Bind()
        
        if (self.EBO):
            glDrawElements(DrawType, len(self.Indices), GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(DrawType, 0, len(self.Vertices))
        
        self.Unbind()