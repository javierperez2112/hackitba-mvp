import model
import gui
import pandas as pd
from PySide6.QtWidgets import QFileDialog
import os
from datetime import datetime

class Data:
    def __init__(self, graph):
        self.emissions_table = {
            "Electricidad (kWh)": 0.429, "Gasolina (L)": 2.26, 
            "Diesel (L)": 2.69, "Bunker (L)": 3.01,
            "Queroseno (L)": 2.48, "LPG (L)": 1.61, 
            "Gasolina de aviacion (L)": 2.69, "Jet Fuel (L)": 2.46
        }
        self.graph = graph
        self.adjacency_list = self._build_adjacency_list()
        self.all_paths = []
        
    def _build_adjacency_list(self):
        """Construye lista de adyacencia para el grafo"""
        adjacency = {}
        for edge in self.graph['edges']:
            if edge['source'] not in adjacency:
                adjacency[edge['source']] = []
            adjacency[edge['source']].append(edge['target'])
        return adjacency
    
    def _find_all_paths(self, current, end, path, visited):
        """Algoritmo DFS recursivo para encontrar todos los caminos"""
        path.append(current)
        visited.add(current)
        
        if current == end:
            self.all_paths.append(list(path))
        else:
            for neighbor in self.adjacency_list.get(current, []):
                if neighbor not in visited:
                    self._find_all_paths(neighbor, end, path, visited)
        
        path.pop()
        visited.remove(current)
    
    def _calculate_emissions(self, path):
        """Calcula las emisiones totales para un camino"""
        total = 0
        for node_name in path:
            node = next(n for n in self.graph['nodes'] if n['name'] == node_name)
            if node['type'] == 'normal':
                energy_type = node['energy_type']
                quantity = node['quantity']
                emission_factor = self.emissions_table.get(energy_type, 0)
                total += quantity * emission_factor
        return total
    
    def process_graph(self):
        """Procesa el grafo y calcula todos los caminos válidos"""
        start_node = next(n['name'] for n in self.graph['nodes'] if n['type'] == 'special' and n['name'] == 'starter')
        end_node = next(n['name'] for n in self.graph['nodes'] if n['type'] == 'special' and n['name'] == 'end')
        
        self._find_all_paths(start_node, end_node, [], set())
        
        # Filtrar caminos que tengan al menos un nodo intermedio
        valid_paths = [path for path in self.all_paths if len(path) > 2]
        
        # Calcular emisiones para cada camino
        ranked_paths = []
        for path in valid_paths:
            emissions = self._calculate_emissions(path)
            ranked_paths.append({
                'path': path,
                'total_emissions': emissions,
                'nodes': len(path) - 2  # Nodos intermedios
            })
        
        # Ordenar por emisiones y luego por cantidad de nodos
        ranked_paths.sort(key=lambda x: (x['total_emissions'], x['nodes']))
        return ranked_paths
    
    def get_ranking(self, top_n=5):
        """Devuelve el ranking formateado"""
        ranked = self.process_graph()
        return ranked[:top_n]
    
    def export_to_excel(self, ranked_paths, filename):
        """Exporta los resultados a un archivo Excel"""
        try:
            # Crear DataFrame
            df = pd.DataFrame([{
                'Ranking': i+1,
                'Ruta': " → ".join(path['path']),
                'Emisiones Totales (ton CO2)': round(path['total_emissions'], 2),
                'Nodos Intermedios': path['nodes']
            } for i, path in enumerate(ranked_paths)])
            
            # Configurar el escritor de Excel
            writer = pd.ExcelWriter(filename, engine='openpyxl')
            df.to_excel(writer, index=False, sheet_name='Resultados')
            
            # Formatear la hoja
            workbook = writer.book
            worksheet = writer.sheets['Resultados']
            
            # Ajustar ancho de columnas
            column_widths = {
                'A': 10,  # Ranking
                'B': 50,  # Ruta
                'C': 20,  # Emisiones
                'D': 15   # Nodos
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
                
            # Guardar y cerrar
            writer.close()
            return True
        except Exception as e:
            print(f"Error al exportar a Excel: {str(e)}")
            return False
