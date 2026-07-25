import glfw
from OpenGL.GL import *
from Entities import BaseEntity

class World:
    def __init__(self, Entities: list[BaseEntity] = None):
        self.Entities: list[BaseEntity] = Entities if Entities is not None else []
        self.RenderableEntites: list[BaseEntity] = []
    
    def RenderEntities(self):
        for Entity in self.RenderableEntites:
            Entity.Render(GL_TRIANGLES)
    
    def AddEntity(self, Entity: BaseEntity):
        self.Entities.append(Entity)
        
        if Entity.Visible:
            self.RenderableEntites.append(Entity)
        
        Entity.PropertyChanged.Connect(lambda Property, Value: self.UpdateEntity(Entity) if Property == "Visible" else None)
    
    def RemoveEntity(self, Entity: BaseEntity):
        self.Entities.remove(Entity)
        
        if Entity.Visible:
            self.RenderableEntites.remove(Entity)
    
    def UpdateEntity(self, Entity):
        if Entity.Visible:
            self.RenderableEntites.append(Entity)
        else:
            self.RenderableEntites.remove(Entity)