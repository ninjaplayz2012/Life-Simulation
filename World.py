import glfw
from OpenGL.GL import *
from Entities import BaseEntity
import bisect

class World:
    def __init__(self, Entities: list[BaseEntity] = None):
        self.Entities: list[BaseEntity] = Entities if Entities is not None else []
        self.RenderableEntites: list[BaseEntity] = []
        self.Rendered = False
    
    def RenderEntities(self):
        for Index in range(len(self.RenderableEntites)):
            self.RenderableEntites[Index].Render(GL_TRIANGLES)
        
        self.Rendered = True
    
    def AddEntity(self, Entity: BaseEntity):
        bisect.insort(self.Entities, Entity)
        
        if Entity.Visible:
            bisect.insort(self.RenderableEntites, Entity)
        
        Entity.PropertyChanged.Connect(lambda Property, Value: self.UpdateEntity(Entity) if Property == "Visible" else None)
    
    def RemoveEntity(self, Entity: BaseEntity):
        self.Entities.remove(Entity)
        
        if Entity.Visible:
            self.RenderableEntites.remove(Entity)
    
    def UpdateEntity(self, Entity):
        if Entity.Visible:
            bisect.insort(self.RenderableEntites, Entity)
        else:
            self.RenderableEntites.remove(Entity)

    def Delete(self):
        for Entity in self.Entities:
            Entity.Delete()
        del self