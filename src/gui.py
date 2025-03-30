import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
from tkinter.ttk import Treeview
import pandas as pd
import model
import backend

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Camaleon PSV Pro")
        self.root.geometry("800x500")
        self.stages = []
        self.titles = []
        root.bind('<Return>', self.update_titles)

        self.frm_buttons = ctk.CTkFrame(root)
        
        self.btn_new = ctk.CTkButton(self.frm_buttons, text="Nueva etapa", command=self.new_stage)
        self.lbl_inst = ctk.CTkLabel(self.frm_buttons, text="Camaleon PSV - inserte etapas del proceso")
        self.btn_run = ctk.CTkButton(self.frm_buttons, text="Ejecutar modelo", command=self.run_model)
        
        self.btn_new.pack(side="left", padx=5, pady=5)
        self.lbl_inst.pack(padx=5, pady=5, side="left")
        self.btn_run.pack(side="right", padx=5, pady=5)

        self.frm_stage = ctk.CTkFrame(root)
        self.frm_buttons.pack(fill="x")
        self.frm_stage.pack(fill="x")

    def new_stage(self):
        new_stage = Stage(self.frm_stage, self, len(self.stages) + 1)
        new_stage.frm.pack(fill="x", padx=5, pady=2)
        self.stages.append(new_stage)

    def remove_stage(self, stage):
        if stage in self.stages:
            self.stages.remove(stage)

    def update_titles(self, event=0):
        self.titles.clear()
        try:
            for stage in self.stages:
                title = stage.title
                if title == "" or title in self.titles:
                    raise ValueError("Títulos no válidos")
                self.titles.append(title)
        except ValueError as e:
            messagebox.showerror("Error: ", str(e))

    def update(self, event):
        for stage in self.stages:
            title = stage.title
            if title == "" or title in self.titles:
                raise ValueError("Títulos no válidos")
            stage.update()
            if not stage.edited:
                raise ValueError("Faltan etapas por rellenar")

    def run_model(self):
        try:
            self.update(0)
        except ValueError as e:
            messagebox.showerror("Error: ", str(e))
            return
        
        data = backend.Data()
        for stage in self.stages:
            data.add_stage(stage)
        
        individual, total = data.apply_model()
        
        # Ocultar ventana principal y mostrar resultados
        self.root.withdraw()
        ResultsWindow(individual, total, self.root)


class Stage:
    def __init__(self, root, app, ord):
        self.app = app
        self.title = f"Stage {ord}"
        self.energy = 100
        self.edited = False

        # Parámetros editables
        self.co2_sup = 0
        self.co2_inf = 0
        self.inv_sup = 0
        self.inv_inf = 0
        self.inv = 0

        self.frm = ctk.CTkFrame(root)
        self.lbl_stage = ctk.CTkLabel(self.frm, text="Etapa:")
        self.ent_stage = ctk.CTkEntry(self.frm)
        self.ent_stage.insert(0, self.title)

        self.lbl_energy = ctk.CTkLabel(self.frm, text="Energía:")
        energy_types = [
            "kWh (Electricidad)", "L (Gasolina)", "L (Diesel)", "L (Bunker)",
            "L (Queroseno)", "L (LPG)", "L (Gasolina de aviacion)", "L (Jet Fuel)"
        ]
        self.cbb_type = ctk.CTkComboBox(self.frm, values=energy_types)
        self.cbb_type.set(energy_types[0])
        self.ent_energy = ctk.CTkEntry(self.frm)
        self.ent_energy.insert(0, str(self.energy))

        self.btn_edit = ctk.CTkButton(self.frm, text="Editar", command=self.open_edit_dialog)
        self.btn_del = ctk.CTkButton(self.frm, text="Eliminar", command=self.destroy)

        self.lbl_stage.pack(side="left", padx=5, pady=5)
        self.ent_stage.pack(side="left", padx=5, pady=5)
        self.lbl_energy.pack(side="left", padx=5, pady=5)
        self.ent_energy.pack(side="left", padx=5, pady=5)
        self.cbb_type.pack(side="left", padx=5, pady=5)
        self.btn_edit.pack(side="left", padx=5, pady=5)
        self.btn_del.pack(side="right", padx=5, pady=5)

    def set_edited(self, val):
        self.edited = val

    def open_edit_dialog(self):
        EditDialog(self)

    def update(self):
        self.title = self.ent_stage.get()
        if self.title == "":
            raise ValueError("Nombre de etapa vacío")
        self.energy = float(self.ent_energy.get())
        if self.energy <= 0:
            raise ValueError(f"Energía inválida en etapa {self.title}")

    def destroy(self):
        self.frm.destroy()
        self.app.remove_stage(self)


class EditDialog:
    def __init__(self, stage):
        self.stage = stage
        self.window = ctk.CTkToplevel()
        self.window.title("Editar Etapa")
        self.window.attributes("-topmost", True)
        self.window.geometry("400x250")
        
        # Labels y entradas para cada parámetro
        fields = [
            ("Límite CO2 Superior", "co2_sup","ton"), ("Límite CO2 Inferior", "co2_inf","ton"),
            ("Límite Inversión Superior", "inv_sup","USD"), ("Límite Inversión Inferior", "inv_inf","USD"), 
            ("Inversión", "inv", "USD")
        ]
        
        self.entries = {}
        for i, (label, var_name, unit) in enumerate(fields):
            ctk.CTkLabel(self.window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ctk.CTkEntry(self.window)
            entry.grid(row=i, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.window, text=unit).grid(row=i, column=2,padx=10, pady=5, sticky="e")
            entry.insert(0, str(getattr(stage, var_name)))  # Cargar valor actual
            self.entries[var_name] = entry
        
        # Botón Guardar
        self.btn_save = ctk.CTkButton(self.window, text="Guardar", command=self.save)
        self.btn_save.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save(self):
        """Guarda los valores editados y los asigna a la etapa con validaciones"""
        try:
            co2_sup = float(self.entries["co2_sup"].get())
            co2_inf = float(self.entries["co2_inf"].get())
            inv_sup = float(self.entries["inv_sup"].get())
            inv_inf = float(self.entries["inv_inf"].get())
            inv = float(self.entries["inv"].get())

            # Validación de rangos
            if co2_inf >= co2_sup:
                raise ValueError("El límite inferior de CO2 debe ser menor que el superior.")
            if inv_inf >= inv_sup:
                raise ValueError("El límite inferior de inversión debe ser menor que el superior.")
            for val in [co2_sup,co2_inf,inv_sup,inv_inf,inv]:
                if val <= 0:
                    raise ValueError("Todos los valores deben ser positivos.")

            # Asignar valores a la etapa
            self.stage.co2_sup = co2_sup
            self.stage.co2_inf = co2_inf
            self.stage.inv_sup = inv_sup
            self.stage.inv_inf = inv_inf
            self.stage.inv = inv

            self.window.destroy()
            self.stage.set_edited(True)

        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))
            self.stage.set_edited(False)

class ResultsWindow(ctk.CTkToplevel):
    def __init__(self, individual, total_emissions, master=None):
        super().__init__(master)
        self.title("Resultados de Emisiones")
        self.geometry("800x600")
        
        # Almacenar datos
        self.individual = individual
        self.total = total_emissions
        
        # Configurar interfaz
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabla de emisiones
        tree_frame = ctk.CTkFrame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=5)
        
        # Configurar Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Etapa", "Emisiones", "Carbon Investment"),
            show="headings",
            selectmode="browse"
        )
        
        # Configurar columnas
        self.tree.heading("Etapa", text="Etapa")
        self.tree.heading("Emisiones", text="Emisiones (kg CO₂)")
        self.tree.heading("Carbon Investment", text="Carbon Investment")
        self.tree.column("Etapa", width=300, anchor="w")
        self.tree.column("Emisiones", width=150, anchor="center")
        self.tree.column("Carbon Investment", width=150, anchor="e")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Insertar datos
        for stage, emissions, metric in self.individual:
            self.tree.insert("", "end", values=(stage, f"{emissions:.2f}", f"{metric:.2f}"))
        
        # Panel inferior
        bottom_frame = ctk.CTkFrame(main_frame)
        bottom_frame.pack(fill="x", pady=10)
        
        # Total
        ctk.CTkLabel(bottom_frame, text="Total de Emisiones:").pack(side="left", padx=10)
        ctk.CTkLabel(bottom_frame, text=f"{self.total:.2f} kg CO₂").pack(side="left")
        
        # Botones
        btn_frame = ctk.CTkFrame(bottom_frame)
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(btn_frame, text="Guardar en Excel", command=self.save_to_excel).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cerrar", command=self.on_close).pack(side="left", padx=5)

    def save_to_excel(self):
        try:
            # Crear DataFrames
            df_individual = pd.DataFrame(
                [(stage, emissions) for stage, emissions in self.individual],
                columns=["Etapa", "Emisiones (kg CO₂)"]
            )
            
            df_total = pd.DataFrame({
                "Total de Emisiones": [self.total]
            })
            
            # Pedir ubicación para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivo Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
            )
            
            if not file_path:
                return  # Usuario canceló
            
            # Guardar en Excel
            with pd.ExcelWriter(file_path) as writer:
                df_individual.to_excel(writer, sheet_name="Emisiones por Etapa", index=False)
                df_total.to_excel(writer, sheet_name="Resumen Total", index=False)
            
            messagebox.showinfo("Éxito", "Datos exportados correctamente a:\n" + file_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def on_close(self):
        self.master.destroy()  # Cerrar aplicación completamente
        #self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    window = ctk.CTk()
    window.iconbitmap("./icon.ico")
    app = App(window)
    window.mainloop()
