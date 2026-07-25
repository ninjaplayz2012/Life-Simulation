import glfw
import numpy as np
import ctypes

from OpenGL.GL import *
from PIL import Image
from Vectors import BaseVector

class Shader:
    def __init__(self, VertexShader: str, FragmentShader: str):
        with open(VertexShader, "r") as Source:
            self.VertexShaderSource = Source.read()
        
        with open(FragmentShader, "r") as Source:
            self.FragmentShaderSource = Source.read()
    
    def Compile(self):
        VertexShader = glCreateShader(GL_VERTEX_SHADER) 
        glShaderSource(VertexShader, self.VertexShaderSource)
        glCompileShader(VertexShader)
        
        FragmentShader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(FragmentShader, self.FragmentShaderSource)
        glCompileShader(FragmentShader)
        
        Good = glGetShaderiv(VertexShader, GL_COMPILE_STATUS)
        if (not Good):
            Log = glGetShaderInfoLog(VertexShader)
            raise RuntimeError(f"Vertex Shader compile error: \n{Log}")
        
        Good = glGetShaderiv(FragmentShader, GL_COMPILE_STATUS)
        if (not Good):
            Log = glGetShaderInfoLog(FragmentShader)
            raise RuntimeError(f"Fragment Shader compile error: \n{Log}")
        
        
        self.Shader = glCreateProgram()
        
        glAttachShader(self.Shader, VertexShader)
        glAttachShader(self.Shader, FragmentShader)
        
        glLinkProgram(self.Shader)

        Good = glGetProgramiv(self.Shader, GL_LINK_STATUS)
        if not Good:
            Log = glGetProgramInfoLog(self.Shader)
            raise RuntimeError(f"Shader link error: \n{Log.decode()}")
        
        glDeleteShader(VertexShader)
        glDeleteShader(FragmentShader)
    
    def Activate(self):
        glUseProgram(self.Shader)
    
    def Delete(self):
        glDeleteProgram(self.Shader)

class Uniform:
    def __init__(self, Location, Setter, Data):
        self.Location = Location
        self.Setter = Setter
        self.Data = Data
    
    def Set(self): 
        self.Setter(self.Location, self.Data)

class Texture:
    def __init__(self, ImagePath: str, TexturePosition, TextureType=GL_TEXTURE_2D):
        self.Texture = None
        self.TexturePosition = TexturePosition
        self.TextureType = TextureType
        self._ImagePath = ImagePath
        self.Generated = False
    
    def Generate(self):
        self.Generated = True
        self.Texture = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0 + self.TexturePosition)
        TempImage = Image.open(self.ImagePath).transpose(Image.FLIP_TOP_BOTTOM)
        ImageData = np.array(TempImage.convert("RGBA"), dtype=np.uint8)
        
        glBindTexture(self.TextureType, self.Texture)
        
        glTexImage2D(
            self.TextureType, 0, GL_RGBA,
            TempImage.width, TempImage.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, ImageData
        )
        
        glTexParameteri(self.TextureType, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(self.TextureType, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(self.TextureType, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(self.TextureType, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glGenerateMipmap(self.TextureType)
    
    def Activate(self):
        glActiveTexture(GL_TEXTURE0 + self.TexturePosition)
        
    def Bind(self):
        glBindTexture(self.TextureType, self.Texture)
    
    def Unbind(self):
        glBindTexture(self.TextureType, 0)
    
    def Delete(self):
        glDeleteTextures(1, [self.Texture]);
        self.Generated = False

    @property
    def ImagePath(self):
        return self._ImagePath
    
    @ImagePath.setter
    def ImagePath(self, Path: str):
        self._ImagePath = Path
        
        if self.Generated:
            self.Delete()
        
        self.Generate()

class VertexBufferObject:
    def __init__(self, Vertices: np.array[np.float32]):
        self.VertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VertexBuffer);
        glBufferData(GL_ARRAY_BUFFER, Vertices.nbytes, Vertices, GL_STATIC_DRAW);
    
    def Bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.VertexBuffer)
    
    def Unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    def Delete(self):
        glDeleteBuffers(1, [self.VertexBuffer])

class VertexArrayObject:
    def __init__(self):
        self.VertexArray = glGenVertexArrays(1)
    
    def LinkAttrib(self, VBO: VertexBufferObject, Layout: int, NumComponents: int, Type: int, Stride: int, Offset: int):
        self.Bind()
        VBO.Bind()
        
        glVertexAttribPointer(Layout, NumComponents, Type, GL_FALSE, Stride, ctypes.c_void_p(Offset))
        glEnableVertexAttribArray(Layout)
        
        VBO.Unbind()
        self.Unbind()
    
    def Bind(self):
        glBindVertexArray(self.VertexArray)
    
    def Unbind(self):
        glBindVertexArray(0)
    
    def Delete(self):
        glDeleteVertexArrays(1, [self.VertexArray])

class ElementArrayBufferObject:
    def __init__(self, Indicies: np.array[np.int32]):
        self.VertexBuffer = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VertexBuffer);
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, Indicies.nbytes, Indicies, GL_STATIC_DRAW);
    
    def Bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.VertexBuffer)
    
    def Unbind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    
    def Delete(self):
        glDeleteBuffers(1, [self.VertexBuffer])
