import glfw
from OpenGL.GL import *
from World import World

class Window:
    def __init__(self, World: World, Size: list[int]):
        # Do the window hints as usual
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        
        self.Window = glfw.create_window(Size[0], Size[1], "Life Simulation", None, None)
        self.Rendering = False
        self.DeltaTime = 0
        self.Size = Size
        self.World = World
        
        if not self.Window:
            glfw.terminate()
            raise RuntimeError("Failed to create the glfw window.")
    
    def Display(self):
        glfw.make_context_current(self.Window)
        glfw.swap_interval(1)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def SetBackgroundColor(self, Red: float, Green: float, Blue: float, Alpha: float):
        glClearColor(Red, Green, Blue, Alpha)
    
    def StartRenderLoop(self, Callback = None):
        self.Rendering = True
        
        CurrentTime = glfw.get_time()
        PreviousTime = glfw.get_time()
        while not glfw.window_should_close(self.Window):
            CurrentTime = glfw.get_time()
            self.DeltaTime = CurrentTime - PreviousTime
            PreviousTime = CurrentTime
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            self.World.RenderEntities()
            if Callback:
                Callback(self.DeltaTime)
            
            glfw.swap_buffers(self.Window)
            glfw.poll_events()
        
        self.Rendering = False