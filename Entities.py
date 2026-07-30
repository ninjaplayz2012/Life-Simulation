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
    
    def Delete(self):
        self.PropertyChanged.Delete()
        del self

# Base Entity class (entites are objects that are rendered) this class holds the properties of all entities
class BaseEntity(BaseObject):
    def __init__(self, ObjectShader: Shader, Vertices: list[BaseVector] = None, Indices: list[int] | None = None, ExtraData: list = None):
        super().__init__()
        
        self.Vertices = Vertices if Vertices else []
        self.Indices = Indices
        self.Position = np.array([0, 0, 0], np.float32)
        self.PositionScale = np.array([0, 0], np.float32)
        self.Scale = 1.0
        self.AnchorPoint = [0.5, 0.5]
        self.ZIndex = 0
        self.Color = [1, 1, 1, 1]
        
        UnpackedVertices = np.concatenate([Vertex.Unpack() for Vertex in Vertices])
        
        if ExtraData is not None:
            UnpackedVertices = np.concatenate([UnpackedVertices, *ExtraData])
        
        self.VAO = VertexArrayObject()
        self.VBO = VertexBufferObject(UnpackedVertices)
        self.EBO = ElementArrayBufferObject(np.array(Indices, np.int32)) if Indices else None
        
        self._Rotation = 0
        self._RotationMatrix = Get2dRotationMatrix(0)
        self._Shader = ObjectShader
        self._Visible = True
        self._Uniforms: list[Uniform] = []
    
    def SetDefaultUniforms(self):
        self.SetUniform("Position", lambda Location, Data : glUniform3f(Location, *self.Position))
        self.SetUniform("PositionScale", lambda Location, Data : glUniform2f(Location, *self.PositionScale))
        self.SetUniform("Scale", lambda Location, Data : glUniform1f(Location, self.Scale))
        self.SetUniform("Rotation", lambda Location, Data : glUniformMatrix2fv(Location, 1, GL_FALSE, self._RotationMatrix))
        self.SetUniform("Anchor", lambda Location, Data : glUniform2f(Location, *self.AnchorPoint))
        self.SetUniform("Size", lambda Location, Data : glUniform2f(Location, *self.Size))
        self.SetUniform("Color", lambda Location, Data : glUniform4f(Location, *self.Color))
    
    def SetUniform(self, Name: str, Setter, Data = None):
        UniformId = glGetUniformLocation(self._Shader.Shader, Name)
        self._Uniforms.append(Uniform(UniformId, Setter, Data))
    
    def GetSize(self, Window):
        Positions = np.array([Vertex.Position[:1] + Vertex.PositionScale * np.array(Window.Size) for Vertex in self.Vertices])  # adjust to however BaseVector exposes position
        MinBound = Positions.min(axis=0)
        MaxBound = Positions.max(axis=0)
        self.Size = (MaxBound - MinBound)[:2].astype(np.float32)
    
    def Generate(self):
        self.VAO.Bind()
        self.VBO.Bind()
        if self.EBO:
            self.EBO.Bind()
        
        Stride = 9 * 4
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, Stride, 0)
        self.VAO.LinkAttrib(self.VBO, 1, 2, GL_FLOAT, Stride, 3 * 4)
        self.VAO.LinkAttrib(self.VBO, 2, 4, GL_FLOAT, Stride, 5 * 4)
        
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

    def Delete(self):
        self.VAO.Delete()
        self.VBO.Delete()
        if self.EBO is ElementArrayBufferObject:
            self.EBO.Delete()
        
        super().Delete()

    def __lt__(self, Other: BaseEntity):
        return self.ZIndex < Other.ZIndex
    
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

def GetValue(Index, List, Default):
    if List is None or len(List) == 0:
        return Default
    if Index >= len(List) or List[Index] is None:
        return Default
    return List[Index]

class InstancedBasedEntity(BaseEntity):
    def __init__(self, ObjectShader, Vertices=None, Indices=None, Instances=1, Divisor=1):
        self._Ready = False
        super().__init__(ObjectShader, Vertices, Indices)
        
        self.Instances = Instances
        self.Divisor = Divisor
        self.InstanceVBO = None
        
        self._Positions = []
        self._PositionScales = []
        self._Scales = []
        self._Rotations = []
        self._Anchors = []
        self._Sizes = []
        self._Colors = []
        
        self._Ready = True
    
    @property
    def Position(self):
        return self._Position
    @Position.setter
    def Position(self, Value):
        self._Position = np.array(Value, np.float32) if not isinstance(Value, np.ndarray) else Value
        if self._Ready: self._Repack()
    
    @property
    def PositionScale(self):
        return self._PositionScale
    @PositionScale.setter
    def PositionScale(self, Value):
        self._PositionScale = Value
        if self._Ready: self._Repack()
    
    @property
    def Scale(self):
        return self._Scale
    @Scale.setter
    def Scale(self, Value):
        self._Scale = Value
        if self._Ready: self._Repack()
    
    @property
    def Rotation(self):
        return self._Rotation
    @Rotation.setter
    def Rotation(self, Value):
        self._Rotation = Value
        self._RotationMatrix = Get2dRotationMatrix(Value)
        self.PropertyChanged.Fire("Rotation", Value)
        if self._Ready: self._Repack()
    
    @property
    def AnchorPoint(self):
        return self._AnchorPoint
    @AnchorPoint.setter
    def AnchorPoint(self, Value):
        self._AnchorPoint = Value
        if self._Ready: self._Repack()
    
    @property
    def Size(self):
        return self._Size
    @Size.setter
    def Size(self, Value):
        self._Size = Value
        if self._Ready: self._Repack()

    @property
    def Color(self):
        return self._Color
    @Color.setter
    def Color(self, Value):
        self._Color = Value
        if self._Ready: self._Repack()
    
    @property
    def Positions(self):
        return self._Positions
    
    @Positions.setter
    def Positions(self, Value):
        self._Positions = Value
        self._Repack()
    
    @property
    def PositionScales(self):
        return self._PositionScales
    
    @PositionScales.setter
    def PositionScales(self, Value):
        self._PositionScales = Value
        self._Repack()
    
    @property
    def Scales(self):
        return self._Scales
    
    @Scales.setter
    def Scales(self, Value):
        self._Scales = Value
        self._Repack()
    
    @property
    def Rotations(self):
        return self._Rotations
    
    @Rotations.setter
    def Rotations(self, Value):
        self._Rotations = Value
        self._Repack()
    
    @property
    def Anchors(self):
        return self._Anchors
    
    @Anchors.setter
    def Anchors(self, Value):
        self._Anchors = Value
        self._Repack()
    
    @property
    def Sizes(self):
        return self._Sizes
    
    @Sizes.setter
    def Sizes(self, Value):
        self._Sizes = Value
        self._Repack()

    @property
    def Colors(self):
        return self._Colors
    @Colors.setter
    def Colors(self, Value):
        self._Colors = Value
        self._Repack()
    
    def UpdateInstanceBasedLists(self):
        self._Positions = []
        self._PositionScales = []
        self._Scales = []
        self._Rotations = []
        self._Anchors = []
        self._Sizes = []
        self._Colors = []
        self._Repack()
    
    def Pack(self):
        FloatsPerInstance = 18
        Data = np.zeros((self.Instances, FloatsPerInstance), dtype=np.float32)
        
        for i in range(self.Instances):
            Data[i, 0:3]   = GetValue(i, self._Positions, self.Position)
            Data[i, 3:5]   = GetValue(i, self._PositionScales, self.PositionScale)
            Data[i, 5]     = GetValue(i, self._Scales, self.Scale)
            Data[i, 10:12] = GetValue(i, self._Anchors, self.AnchorPoint)
            Data[i, 12:14] = GetValue(i, self._Sizes, self.Size)
            Data[i, 14:18] = GetValue(i, self._Colors, self.Color)
            
            Rotation = GetValue(i, self._Rotations, None)
            Data[i, 6:10] = Get2dRotationMatrix(Rotation).flatten() if Rotation is not None else self._RotationMatrix.flatten()
        
        return Data.flatten()
    
    def _Repack(self):
        """Re-pack instance data and push it straight into the existing GPU buffer, if it exists."""
        if not self._Ready or self.InstanceVBO is None:
            return
        
        PackedData = self.Pack()
        self.InstanceVBO.Bind()
        self.InstanceVBO.SetData(PackedData, GL_DYNAMIC_DRAW)
        self.InstanceVBO.Unbind()
    
    def Generate(self):
        VertexStride = 9 * 4
        
        self.VAO.Bind()
        self.VBO.Bind()
        if self.EBO:
            self.EBO.Bind()
        
        self.VAO.Divisor = 0
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, VertexStride, 0 * 4)  # aPosition
        self.VAO.LinkAttrib(self.VBO, 1, 2, GL_FLOAT, VertexStride, 3 * 4)  # aPositionScale
        self.VAO.LinkAttrib(self.VBO, 2, 4, GL_FLOAT, VertexStride, 5 * 4)  # aColor
        
        self.VAO.Unbind()
    
    def GenerateInstances(self):
        PackedData = self.Pack()
        self.InstanceVBO = VertexBufferObject(PackedData, GL_DYNAMIC_DRAW)
        
        self.VAO.Bind()
        self.InstanceVBO.Bind()
        
        InstanceStride = 18 * 4
        self.VAO.Divisor = self.Divisor
        self.VAO.LinkAttrib(self.InstanceVBO, 3, 3, GL_FLOAT, InstanceStride, 0  * 4)  # iPosition
        self.VAO.LinkAttrib(self.InstanceVBO, 4, 2, GL_FLOAT, InstanceStride, 3  * 4)  # iPositionScale
        self.VAO.LinkAttrib(self.InstanceVBO, 5, 1, GL_FLOAT, InstanceStride, 5  * 4)  # iScale
        self.VAO.LinkAttrib(self.InstanceVBO, 6, 2, GL_FLOAT, InstanceStride, 6  * 4)  # iRotation col1
        self.VAO.LinkAttrib(self.InstanceVBO, 7, 2, GL_FLOAT, InstanceStride, 8  * 4)  # iRotation col2
        self.VAO.LinkAttrib(self.InstanceVBO, 8, 2, GL_FLOAT, InstanceStride, 10 * 4)  # iAnchor
        self.VAO.LinkAttrib(self.InstanceVBO, 9, 2, GL_FLOAT, InstanceStride, 12 * 4)  # iSize
        self.VAO.LinkAttrib(self.InstanceVBO, 10, 4, GL_FLOAT, InstanceStride, 14 * 4) # iColor
        
        self.VAO.Unbind()
        self._Ready = True
    
    def Render(self, DrawType):
        self._Shader.Activate()
        self.Bind()
        
        for Uniform in self._Uniforms:
            Uniform.Set()
        
        if self.EBO:
            glDrawElementsInstanced(DrawType, len(self.Indices), GL_UNSIGNED_INT, None, self.Instances)
        else:
            glDrawArraysInstanced(DrawType, 0, len(self.Vertices), self.Instances)
        
        self.Unbind()
    
    def Delete(self):
        if self.InstanceVBO:
            self.InstanceVBO.Delete()
        super().Delete()

class ImageEntity(BaseEntity):
    def __init__(self, ImagePaths: list[str], ObjectShader: Shader, Vertices: list[BaseVector] = [], Indices: list[int] | None = None):
        super().__init__(ObjectShader, Vertices, Indices)
        
        if isinstance(ImagePaths, str):
            ImagePaths = [ImagePaths]

        self.CurrentTexture = 0
        self._Textures = [Texture(Path, Index) for Index, Path in enumerate(ImagePaths)]
        self.SetUniform("CurrentTexture", lambda Location, Data : glUniform1i(Location, self.CurrentTexture))
    
    def Generate(self):
        for Texture in self._Textures:
            Texture.Generate()
        
        Stride = 11 * 4
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, Stride, 0)
        self.VAO.LinkAttrib(self.VBO, 1, 2, GL_FLOAT, Stride, 3 * 4)
        self.VAO.LinkAttrib(self.VBO, 2, 2, GL_FLOAT, Stride, 5 * 4)
        self.VAO.LinkAttrib(self.VBO, 3, 4, GL_FLOAT, Stride, 7 * 4)
    
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
    
    def Delete(self):
        for Texture in self._Textures:
            Texture.Delete()
        super().Delete()

class ImageInstancedBasedEntity(InstancedBasedEntity):
    def __init__(self, ImagePaths: list[str], ObjectShader, Vertices=None, Indices=None, Instances=1, Divisor=1):
        super().__init__(ObjectShader, Vertices, Indices, Instances, Divisor)
        
        self._Textures = [Texture(Path, Index) for Index, Path in enumerate(ImagePaths)]
        self.CurrentTexture = 0
        self.SetUniform("CurrentTexture", lambda Location, Data : glUniform1i(Location, self.CurrentTexture))
    
    def Generate(self):
        for Texture in self._Textures:
            Texture.Generate()
        
        Stride = 11 * 4
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, Stride, 0)
        self.VAO.LinkAttrib(self.VBO, 1, 2, GL_FLOAT, Stride, 3 * 4)
        self.VAO.LinkAttrib(self.VBO, 2, 2, GL_FLOAT, Stride, 5 * 4)
        self.VAO.LinkAttrib(self.VBO, 3, 4, GL_FLOAT, Stride, 7 * 4)
    
    def GenerateInstances(self):
        PackedData = self.Pack()
        self.InstanceVBO = VertexBufferObject(PackedData, GL_DYNAMIC_DRAW)
        
        self.VAO.Bind()
        self.InstanceVBO.Bind()
        
        InstanceStride = 18 * 4
        self.VAO.Divisor = self.Divisor
        self.VAO.LinkAttrib(self.InstanceVBO, 4, 3, GL_FLOAT, InstanceStride, 0  * 4)  # iPosition
        self.VAO.LinkAttrib(self.InstanceVBO, 5, 2, GL_FLOAT, InstanceStride, 3  * 4)  # iPositionScale
        self.VAO.LinkAttrib(self.InstanceVBO, 6, 1, GL_FLOAT, InstanceStride, 5  * 4)  # iScale
        self.VAO.LinkAttrib(self.InstanceVBO, 7, 2, GL_FLOAT, InstanceStride, 6  * 4)  # iRotation col1
        self.VAO.LinkAttrib(self.InstanceVBO, 8, 2, GL_FLOAT, InstanceStride, 8  * 4)  # iRotation col2
        self.VAO.LinkAttrib(self.InstanceVBO, 9, 2, GL_FLOAT, InstanceStride, 10 * 4)  # iAnchor
        self.VAO.LinkAttrib(self.InstanceVBO, 10, 2, GL_FLOAT, InstanceStride, 12 * 4)  # iSize
        self.VAO.LinkAttrib(self.InstanceVBO, 11, 4, GL_FLOAT, InstanceStride, 14 * 4) # iColor
        
        self.VAO.Unbind()
        self._Ready = True
    
    def Render(self, DrawType):
        self._Shader.Activate()
        self.Bind()
        
        for Uniform in self._Uniforms:
            Uniform.Set()
        
        for Texture in self._Textures:
            Texture.Activate()
            Texture.Bind()
        
        if self.EBO:
            glDrawElementsInstanced(DrawType, len(self.Indices), GL_UNSIGNED_INT, None, self.Instances)
        else:
            glDrawArraysInstanced(DrawType, 0, len(self.Vertices), self.Instances)
        
        self.Unbind()
    
    def Delete(self):
        for Texture in self._Textures:
            Texture.Delete()
        super().Delete()

class ArrayEntity(InstancedBasedEntity):
    def __init__(self, ObjectShader, Rows=1, Columns=1, Skip=None, Vertices=None, Indices=None, Divisor=1, EveryOther=False):
        TotalSlots = Rows * Columns
        
        if Skip is not None:
            SkipOccurrences = TotalSlots // Skip
            if EveryOther:
                DroppedCount = SkipOccurrences // 2 + (SkipOccurrences % 2)  # odd occurrences get dropped
            else:
                DroppedCount = SkipOccurrences
        else:
            DroppedCount = 0
        
        Instances = TotalSlots - DroppedCount
        
        super().__init__(ObjectShader, Vertices, Indices, Instances, Divisor)
        
        self.Rows = Rows
        self.Columns = Columns
        self.Skip = Skip
        self.EveryOther = EveryOther
        self.Offset = [0, 0, 0, 0]
    
    def BuildGridPositions(self):
        """Walk every row/col slot, skip every Nth, and if EveryOther, only skip every other skip-occurrence."""
        Positions = []
        PositionScales = []
        SlotIndex = 0
        SkipOccurrences = 0  # counts how many times we've HIT a skip-slot, regardless of whether we actually skipped
        
        for Row in range(self.Rows):
            for Col in range(self.Columns):
                IsSkipSlot = self.Skip is not None and (SlotIndex + 1) % self.Skip == 0
                
                if IsSkipSlot:
                    SkipOccurrences += 1
                    ShouldActuallySkip = (not self.EveryOther) or (SkipOccurrences % 2 == 1)
                    
                    if ShouldActuallySkip:
                        SlotIndex += 1
                        continue
                
                XOffset, XScale = self.Position[0] + Col * self.Offset[0], self.PositionScale[0] + Col * self.Offset[2]
                YOffset, YScale = self.Position[1] + Row * self.Offset[1], self.PositionScale[1] + Row * self.Offset[3]
                Positions.append([XOffset, YOffset, self.Position[2]])
                PositionScales.append([XScale, YScale])
                
                SlotIndex += 1
        
        return np.array(Positions, dtype=np.float32), np.array(PositionScales, dtype=np.float32)

    def GenerateInstances(self):
        self.Positions, self.PositionScales = self.BuildGridPositions()
        super().GenerateInstances()

class ImageArrayEntity(ArrayEntity):
    def __init__(self, ImagePaths, ObjectShader, Rows=1, Columns=1, Skip=None, Vertices=None, Indices=None, Divisor=1, EveryOther=False):
        super().__init__(ObjectShader, Rows, Columns, Skip, Vertices, Indices, Divisor, EveryOther)
        
        self.CurrentTexture = 0
        self._Textures = [Texture(Path, Index) for Index, Path in enumerate(ImagePaths)]
        self.SetUniform("CurrentTexture", lambda Location, Data : glUniform1i(Location, self.CurrentTexture))
        
    def Generate(self):
        for Texture in self._Textures:
            Texture.Generate()
        
        Stride = 11 * 4
        self.VAO.LinkAttrib(self.VBO, 0, 3, GL_FLOAT, Stride, 0)
        self.VAO.LinkAttrib(self.VBO, 1, 2, GL_FLOAT, Stride, 3 * 4)
        self.VAO.LinkAttrib(self.VBO, 2, 2, GL_FLOAT, Stride, 5 * 4)
        self.VAO.LinkAttrib(self.VBO, 4, 3, GL_FLOAT, Stride, 7 * 4)
    
    def GenerateInstances(self):
        PackedData = self.Pack()
        self.InstanceVBO = VertexBufferObject(PackedData, GL_DYNAMIC_DRAW)
        
        self.VAO.Bind()
        self.InstanceVBO.Bind()
        
        InstanceStride = 18 * 4
        self.VAO.Divisor = self.Divisor
        self.VAO.LinkAttrib(self.InstanceVBO, 4, 3, GL_FLOAT, InstanceStride, 0  * 4)  # iPosition
        self.VAO.LinkAttrib(self.InstanceVBO, 5, 2, GL_FLOAT, InstanceStride, 3  * 4)  # iPositionScale
        self.VAO.LinkAttrib(self.InstanceVBO, 6, 1, GL_FLOAT, InstanceStride, 5  * 4)  # iScale
        self.VAO.LinkAttrib(self.InstanceVBO, 7, 2, GL_FLOAT, InstanceStride, 6  * 4)  # iRotation col1
        self.VAO.LinkAttrib(self.InstanceVBO, 8, 2, GL_FLOAT, InstanceStride, 8  * 4)  # iRotation col2
        self.VAO.LinkAttrib(self.InstanceVBO, 9, 2, GL_FLOAT, InstanceStride, 10 * 4)  # iAnchor
        self.VAO.LinkAttrib(self.InstanceVBO, 10, 2, GL_FLOAT, InstanceStride, 12 * 4)  # iSize
        self.VAO.LinkAttrib(self.InstanceVBO, 11, 4, GL_FLOAT, InstanceStride, 14 * 4) # iColor
        
        self.VAO.Unbind()
        self._Ready = True
    
    def Render(self, DrawType):
        self._Shader.Activate()
        self.Bind()
        
        for Uniform in self._Uniforms:
            Uniform.Set()
        
        for Texture in self._Textures:
            Texture.Activate()
            Texture.Bind()
        
        if self.EBO:
            glDrawElementsInstanced(DrawType, len(self.Indices), GL_UNSIGNED_INT, None, self.Instances)
        else:
            glDrawArraysInstanced(DrawType, 0, len(self.Vertices), self.Instances)
        
        self.Unbind()
    
    def Delete(self):
        for Texture in self._Textures:
            Texture.Delete()
        super().Delete()