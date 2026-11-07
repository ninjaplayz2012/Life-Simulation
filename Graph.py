import matplotlib.pyplot as plt
import matplotlib.cm as cm
import itertools
import numpy as np

# Note: This script was written by AI to collect data and I was too lazy to actually make this.

Mocha = {
    "Base":     "#1e1e2e",
    "Surface":  "#313244",
    "Text":     "#cdd6f4",
    "Subtext":  "#a6adc8",
    "Red":      "#f38ba8",
    "Green":    "#a6e3a1",
    "Peach":    "#fab387",
    "Lavender": "#b4befe",
}

AccentCycle = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#94e2d5",
               "#89b4fa", "#cba6f7", "#f5c2e7", "#eba0ac", "#b4befe"]

class StatsRecorder:
    def __init__(self):
        self.ElapsedTime = 0.0
        self.Times = []
        self.GremlinCounts = []
        self.BushCounts = []
        self.BushesWithBerries = []
        self.BushesWithoutBerries = []
        self.AverageHungerValues = []
        self.GremlinHistory = {}
    
    def Record(self, DeltaTime, Gremlins, Bushes):
        self.ElapsedTime += DeltaTime
        self.Times.append(self.ElapsedTime)
        self.GremlinCounts.append(len(Gremlins))
        self.BushCounts.append(len(Bushes))
        
        WithBerries = sum(1 for Bush in Bushes if not Bush.Regrowing)
        WithoutBerries = sum(1 for Bush in Bushes if Bush.Regrowing)
        self.BushesWithBerries.append(WithBerries)
        self.BushesWithoutBerries.append(WithoutBerries)
        
        CurrentNames = set()
        HungerValuesThisFrame = []
        
        for Gremlin in Gremlins:
            CurrentNames.add(Gremlin.Name)
            HungerValuesThisFrame.append(Gremlin.Hunger)
            
            if Gremlin.Name not in self.GremlinHistory:
                self.GremlinHistory[Gremlin.Name] = [None] * (len(self.Times) - 1)
            
            self.GremlinHistory[Gremlin.Name].append(Gremlin.Hunger)
        
        for Name in self.GremlinHistory:
            if Name not in CurrentNames:
                self.GremlinHistory[Name].append(None)
        
        self.AverageHungerValues.append(np.mean(HungerValuesThisFrame) if HungerValuesThisFrame else None)
    
    def Show(self):
        plt.rcParams.update({
            "figure.facecolor": Mocha["Base"],
            "axes.facecolor": Mocha["Surface"],
            "axes.edgecolor": Mocha["Subtext"],
            "axes.labelcolor": Mocha["Text"],
            "text.color": Mocha["Text"],
            "xtick.color": Mocha["Subtext"],
            "ytick.color": Mocha["Subtext"],
            "grid.color": Mocha["Surface"],
            "font.family": "monospace",
            "font.size": 10,
        })
        
        Fig, (PopAx, BerryAx, HungerAx) = plt.subplots(3, 1, figsize=(9, 11))
        Fig.canvas.manager.set_window_title("Life Simulation Stats")
        
        # --- Population subplot ---
        PopAx.plot(self.Times, self.GremlinCounts, label="Gremlins", color=Mocha["Red"], linewidth=2)
        PopAx.plot(self.Times, self.BushCounts, label="Bushes", color=Mocha["Green"], linewidth=2)
        PopAx.set_ylabel("Count")
        PopAx.set_title("Population Over Time", fontsize=12, fontweight="bold", color=Mocha["Text"])
        PopAx.grid(True, alpha=0.3)
        PopAx.legend(loc="upper right", framealpha=0.9, facecolor=Mocha["Surface"], edgecolor=Mocha["Subtext"])
        for Spine in PopAx.spines.values():
            Spine.set_color(Mocha["Subtext"])
        
        # --- Berry availability subplot ---
        BerryAx.plot(self.Times, self.BushesWithBerries, label="With Berries",
                     color=Mocha["Peach"], linewidth=2)
        BerryAx.plot(self.Times, self.BushesWithoutBerries, label="Without Berries (Regrowing)",
                     color=Mocha["Subtext"], linewidth=2, linestyle=":")
        BerryAx.set_ylabel("Bush Count")
        BerryAx.set_title("Bush Berry Availability", fontsize=12, fontweight="bold", color=Mocha["Text"])
        BerryAx.grid(True, alpha=0.3)
        BerryAx.legend(loc="upper right", framealpha=0.9, facecolor=Mocha["Surface"], edgecolor=Mocha["Subtext"])
        for Spine in BerryAx.spines.values():
            Spine.set_color(Mocha["Subtext"])
        
        # --- Hunger subplot ---
        ColorPool = itertools.cycle(AccentCycle)
        for Name, Values in self.GremlinHistory.items():
            HungerAx.plot(self.Times, Values, label=Name, color=next(ColorPool), linewidth=1, alpha=0.55)
        
        HungerAx.plot(self.Times, self.AverageHungerValues, label="Average",
                       color=Mocha["Lavender"], linewidth=3, linestyle="--", zorder=10)
        
        HungerAx.axhline(y=75, color=Mocha["Peach"], linewidth=1.5, linestyle="-.",
                          alpha=0.8, zorder=9, label="Seek Food Threshold")
        
        HungerAx.set_ylabel("Hunger")
        HungerAx.set_xlabel("Time (s)")
        HungerAx.set_title("Hunger by Gremlin", fontsize=12, fontweight="bold", color=Mocha["Text"])
        HungerAx.grid(True, alpha=0.3)
        NumCols = max(1, (len(self.GremlinHistory) + 1) // 12 + 1)
        HungerAx.legend(loc="upper right", fontsize=8, ncol=NumCols,
                         framealpha=0.9, facecolor=Mocha["Surface"], edgecolor=Mocha["Subtext"])
        for Spine in HungerAx.spines.values():
            Spine.set_color(Mocha["Subtext"])
        
        Fig.tight_layout()
        plt.show()

class LiveGraph:
    def __init__(self, HistoryLength=200):
        plt.ion()
        self.Fig, (self.PopAx, self.HungerAx) = plt.subplots(2, 1, figsize=(7, 6))
        self.Fig.canvas.manager.set_window_title("Live Stats")
        
        self.Fig.patch.set_facecolor(Mocha["Base"])
        for Ax in (self.PopAx, self.HungerAx):
            Ax.set_facecolor(Mocha["Surface"])
            Ax.tick_params(colors=Mocha["Subtext"])
            for Spine in Ax.spines.values():
                Spine.set_color(Mocha["Subtext"])
        
        self.HistoryLength = HistoryLength
        self.Times = []
        self.GremlinCounts = []
        self.BushCounts = []
        self.AverageHungerValues = []
        
        self.GremlinLine, = self.PopAx.plot([], [], color=Mocha["Red"], linewidth=2, label="Gremlins")
        self.BushLine, = self.PopAx.plot([], [], color=Mocha["Green"], linewidth=2, label="Bushes")
        self.PopAx.set_ylabel("Count", color=Mocha["Text"])
        self.PopAx.legend(loc="upper right", fontsize=8, facecolor=Mocha["Surface"], edgecolor=Mocha["Subtext"], labelcolor=Mocha["Text"])
        
        self.AverageLine, = self.HungerAx.plot([], [], color=Mocha["Lavender"], linewidth=2, label="Average Hunger")
        self.HungerAx.axhline(y=50, color=Mocha["Peach"], linewidth=1, linestyle="-.", alpha=0.7)
        self.HungerAx.set_ylabel("Hunger", color=Mocha["Text"])
        self.HungerAx.set_xlabel("Time (s)", color=Mocha["Text"])
        self.HungerAx.legend(loc="upper right", fontsize=8, facecolor=Mocha["Surface"], edgecolor=Mocha["Subtext"], labelcolor=Mocha["Text"])
        
        self.Fig.tight_layout()
        self.Fig.canvas.draw()
        self.Background = self.Fig.canvas.copy_from_bbox(self.Fig.bbox)  # for blitting
    
    def Update(self, ElapsedTime, Gremlins, Bushes):
        self.Times.append(ElapsedTime)
        self.GremlinCounts.append(len(Gremlins))
        self.BushCounts.append(len(Bushes))
        
        Hungers = [Gremlin.Hunger for Gremlin in Gremlins]
        self.AverageHungerValues.append(np.mean(Hungers) if Hungers else 0)
        
        if len(self.Times) > self.HistoryLength:
            self.Times = self.Times[-self.HistoryLength:]
            self.GremlinCounts = self.GremlinCounts[-self.HistoryLength:]
            self.BushCounts = self.BushCounts[-self.HistoryLength:]
            self.AverageHungerValues = self.AverageHungerValues[-self.HistoryLength:]
        
        self.GremlinLine.set_data(self.Times, self.GremlinCounts)
        self.BushLine.set_data(self.Times, self.BushCounts)
        self.AverageLine.set_data(self.Times, self.AverageHungerValues)
        
        self.PopAx.relim()
        self.PopAx.autoscale_view()
        self.HungerAx.relim()
        self.HungerAx.autoscale_view()
        
        self.Fig.canvas.draw_idle()
        self.Fig.canvas.flush_events()