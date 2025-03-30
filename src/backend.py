import gui
import model
import pandas as pd
import matplotlib as plt
import numpy as np
import customtkinter as ctk

class Data:
    def __init__(self):
        self.stages = []  # Inicializar como lista vacía
        self.emissions_table = {
            "kWh (Electricidad)": 0.429, 
            "L (Gasolina)": 2.26,
            "L (Diesel)": 2.69, 
            "L (Bunker)": 3.01,
            "L (Queroseno)": 2.48, 
            "L (LPG)": 1.61,
            "L (Gasolina de aviacion)": 2.69, 
            "L (Jet Fuel)": 2.46
        }
    
    def calculate_emissions(self, stage: gui.Stage):
        energy_type = stage.cbb_type.get()  # Acceder al tipo de energía almacenado
        return self.emissions_table[energy_type] * stage.energy

    def add_stage(self, stage: gui.Stage):
        emissions = self.calculate_emissions(stage)
        self.stages.append((stage, emissions))  # Guardar tupla (instancia, valor)

    def apply_model(self):
        individual = []
        total_emissions = 0.0
        
        for stage, emissions in self.stages:  # Ahora sí puede desempaquetar
            individual.append((stage.title,emissions,model.evaluate_carbon_investment(emissions / 1000, stage.inv, 
                                                                 stage.co2_inf, stage.co2_sup,
                                                                 stage.inv_inf, stage.inv_sup,
                                                                 0.8, 0.2)))
            total_emissions += emissions
        
        return individual, total_emissions