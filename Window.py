import glfw
from OpenGL.GL import *
from World import World
import numpy as np

class Window:
    def __init__(self, World: World, Size: list[int], FullscreenMonitor=None):
        # Do the window hints as usual
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

        self.Monitor = FullscreenMonitor if FullscreenMonitor is not None else glfw.get_primary_monitor()
        self.Mode = glfw.get_video_mode(self.Monitor);
        
        glfw.window_hint(glfw.RED_BITS, self.Mode.bits.red);
        glfw.window_hint(glfw.GREEN_BITS, self.Mode.bits.green);
        glfw.window_hint(glfw.BLUE_BITS, self.Mode.bits.blue);
        glfw.window_hint(glfw.REFRESH_RATE, self.Mode.refresh_rate);
        
        self.Window = glfw.create_window(Size[0], Size[1], "Life Simulation", FullscreenMonitor, None)
        if not self.Window:
            glfw.terminate()
            raise RuntimeError("Failed to create the glfw window.")
        
        self.Rendering = False
        self.DeltaTime = 0
        self.World = World
        self.Shaders = []
        self._Size = Size
    
    def Display(self):
        glfw.make_context_current(self.Window)
        glfw.swap_interval(1)

        glViewport(0, 0, *self.Size)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def Maximize(self):
        glfw.maximize_window(self.Window)
        self.Size = [self.Mode.size.width, self.Mode.size.height]
    
    def SetBackgroundColor(self, Red: float, Green: float, Blue: float, Alpha: float):
        glClearColor(Red, Green, Blue, Alpha)
    
    def SetBackgroundColorHex(self, HexCode: str):
        HexCode = HexCode[1:] # Remove the "#" from the hex code
        Red, Green, Blue, Alpha = int("0x" + HexCode[:2], 16), int("0x" + HexCode[2:4], 16), int("0x" + HexCode[4:6], 16), int("0x" + HexCode[6:8], 16)
        glClearColor(Red / 255, Green / 255, Blue / 255, Alpha / 255)
    
    def Update(self, Shaders: list):
        self.Shaders = np.concatenate([Shaders, self.Shaders])
        for Shader in self.Shaders:
            Shader.Compile()
            Shader.SetGlobalUniform("WindowSize", lambda Location, Data : glUniform2f(Location, *self.Size))
        
        glfw.set_framebuffer_size_callback(self.Window, lambda Win, Wid, Hei : self.ChangeSize([Wid, Hei]))
    
    def ChangeSize(self, Size: list[int]):
        self.Size = Size
        
        for Entity in self.World.Entities:
            Entity.GetSize(self)
    
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
    
    def Delete(self):
        glfw.destroy_window(self.Window)
        self.World.Delete()
        del self
    
    @property
    def Size(self):
        return self._Size

    @Size.setter
    def Size(self, Size: list[int]):
        glViewport(0, 0, Size[0], Size[1])
        self._Size = Size