from perlin_numpy import generate_fractal_noise_2d
import numpy as np
from Entities import ImageEntity, Texture, Shader, BaseVector
from Window import Window
from PIL import Image
import time

class WorldGenerator:
    def __init__(self, Window: Window, Seed=None):
        self.Map = None
        self.Window = Window
        self.Seed = Seed
        self.Generator = np.random.RandomState(seed=self.Seed)
        self.ShaderProgram = None
    
    def GenerateNoise(self, Size, Resolution=1, Lacunarity=1, Octaves=1, Persistance=0.5):
        NoiseMatrix = generate_fractal_noise_2d(shape=(Size[0], Size[1]), lacunarity=Lacunarity, octaves=Octaves, res=(Resolution, Resolution), persistence=Persistance, rng=self.Generator)
        NormalizedNoise = np.clip((NoiseMatrix + 1) * 0.5, 0, 1)
        Pixels = np.zeros((Size[0], Size[1], 3), dtype=np.uint8)
        
        MapHeight, MapWidth = NormalizedNoise.shape
        RgbPixels = np.zeros((MapHeight, MapWidth, 3), dtype=np.uint8)
        
        # Define precise RGB color milestones
        ColorBlue   = np.array([0, 0, 255])
        ColorLightBlue   = np.array([0, 200, 255])
        ColorSand   = np.array([240, 220, 130])
        ColorGreen  = np.array([0, 255, 0])
        ColorGrey   = np.array([128, 128, 128])
        ColorWhite  = np.array([255, 255, 255])
        
        MaskWater = NormalizedNoise <= 0.1
        TWater = (NormalizedNoise[MaskWater] - 0.0) / 0.1
        RgbPixels[MaskWater] = (1 - TWater)[:, None] * ColorBlue + TWater[:, None] * ColorLightBlue
        
        MaskShallowWater = (NormalizedNoise > 0.1) & (NormalizedNoise <= 0.3)
        TShallowWater = (NormalizedNoise[MaskShallowWater] - 0.1) / 0.2
        TShallowWaterExp = TShallowWater ** 2  
        RgbPixels[MaskShallowWater] = (1 - TShallowWaterExp)[:, None] * ColorLightBlue + TShallowWaterExp[:, None] * ColorSand
        
        MaskBeach = (NormalizedNoise > 0.3) & (NormalizedNoise <= 0.4)
        TBeach = (NormalizedNoise[MaskBeach] - 0.3) / 0.1
        RgbPixels[MaskBeach] = (1 - TBeach)[:, None] * ColorSand + TBeach[:, None] * ColorGreen
        
        MaskGrass = (NormalizedNoise > 0.4) & (NormalizedNoise <= 0.7)
        TGrass = (NormalizedNoise[MaskGrass] - 0.4) / 0.3
        RgbPixels[MaskGrass] = (1 - TGrass)[:, None] * ColorGreen + TGrass[:, None] * ColorGrey
        
        MaskSnow = NormalizedNoise > 0.7
        TSnow = (NormalizedNoise[MaskSnow] - 0.7) / 0.3
        RgbPixels[MaskSnow] = (1 - TSnow)[:, None] * ColorGrey + TSnow[:, None] * ColorWhite
        
        self.Pixels = RgbPixels

    def GenerateMap(self):
        Img = Image.fromarray(self.Pixels)
        Img.save("./Resources/Noise.png")
        Tex = Texture()
        Tex.Image = Img
        
        Vertices = [
            BaseVector(PositionScale=[0, 1], TexCoord=[0.0, 1.0]),
            BaseVector(PositionScale=[0, 0], TexCoord=[0.0, 0.0]),
            BaseVector(PositionScale=[1, 0], TexCoord=[1.0, 0.0]),
            BaseVector(PositionScale=[1, 1], TexCoord=[1.0, 1.0])
        ]
        
        self.Map = ImageEntity([], self.ShaderProgram, Vertices, [0, 1, 2, 0, 2, 3])
        self.Map._Textures = [Tex]
        self.Map.AnchorPoint = [0, 0]
        self.Map.SetDefaultUniforms()
        self.Map.GetSize(self.Window)
        self.Map.Generate()
        self.Window.World.AddEntity(self.Map)