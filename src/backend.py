import gui
import model
import pandas as pd
import matplotlib as plt
import numpy as np

class Data:
    def __init__(self):
        self.stages = list((gui.Stage, float))
        self.emissions_table = {
            "kWh (Electricidad)":0.429, "L (Gasolina)":2.26, "L (Diesel)":2.69, "L (Bunker)":3.01,
            "L (Queroseno)":2.48, "L (LPG)":1.61, "L (Gasolina de aviacion)":2.69,"L (Jet Fuel)":2.46
        }
    
    def calculate_emissions(self, stage: gui.Stage):
        energy_type = str(stage.cbb_type.get())
        emissions = self.emissions_table[energy_type] * stage.energy
        print(emissions)
        return emissions

    def add_stage(self, stage: gui.Stage):
        self.stages.append((stage, self.calculate_emissions(stage)))

    def apply_model(self):
        return
