import sys
import math
from PySide6.QtCore import Qt, QRectF, QPointF, QLineF, QSize, QLocale
from PySide6.QtGui import (QPainter, QPen, QBrush, QColor, QAction, QCursor, 
                          QDoubleValidator, QPolygonF, QPainterPath, QPalette)
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
                              QGraphicsEllipseItem, QGraphicsTextItem, QToolBar, QDialog,
                              QVBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsPathItem,
                              QWidget, QHBoxLayout, QTextEdit, QComboBox, QFormLayout, QMessageBox)
import pandas as pd
from PySide6.QtWidgets import QFileDialog
import backend
import os
from datetime import datetime

class NodeDialog(QDialog):
    """Diálogo para editar las propiedades de un nodo normal (no especial)"""
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.parent = parent
        self.setWindowTitle(f"Propiedades del Nodo: {node.name}")
        self.setModal(True)
        
        # Configuración del layout principal
        self.setup_ui()
        
    def setup_ui(self):
        """Configura todos los elementos de la interfaz del diálogo"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Campos del formulario
        self.setup_form_fields()
        
        # Botones de acción
        self.setup_action_buttons()
        
        self.setLayout(self.layout)
        self.resize(450, 450)
    
    def setup_form_fields(self):
        """Configura los campos del formulario"""
        self.form_layout = QFormLayout()
        
        # Campo de nombre
        self.name_input = QLineEdit(self.node.name)
        self.form_layout.addRow("Nombre del nodo:", self.name_input)
        
        # Campo de tipo de energía
        self.setup_energy_type_field()
        
        # Campo de cantidad
        self.setup_quantity_field()
        
        # Sección CO2
        self.setup_co2_section()
        
        # Sección Inversión
        self.setup_investment_section()
        
        # Campo de descripción
        self.setup_description_field()
        
        self.layout.addLayout(self.form_layout)
    
    def setup_energy_type_field(self):
        """Configura el combo box de tipos de energía"""
        self.energy_type = QComboBox()
        energy_types = [
            "Electricidad (kWh)",
            "Gasolina (L)",
            "Diesel (L)",
            "Bunker (L)",
            "Queroseno (L)",
            "LPG (L)",
            "Gasolina de aviacion (L)",
            "Jet Fuel (L)"
        ]
        self.energy_type.addItems(energy_types)
        if self.node.energy_type in energy_types:
            self.energy_type.setCurrentText(self.node.energy_type)
        self.form_layout.addRow("Tipo de energia:", self.energy_type)
    
    def setup_quantity_field(self):
        """Configura el campo de cantidad con validación"""
        self.quantity = QLineEdit(str(self.node.quantity).replace('.', ','))
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        locale = validator.locale()
        locale.setNumberOptions(locale.numberOptions() | QLocale.RejectGroupSeparator)
        validator.setLocale(locale)
        self.quantity.setValidator(validator)
        self.form_layout.addRow("Cantidad:", self.quantity)
    
    def setup_co2_section(self):
        """Configura la sección de límites de CO2"""
        # Etiquetas
        co2_label_layout = QHBoxLayout()
        co2_label_layout.addWidget(QLabel("Límite inferior de CO2 (ton)"))
        co2_label_layout.addWidget(QLabel("Límite superior de CO2 (ton)"))
        self.form_layout.addRow(co2_label_layout)
        
        # Campos de entrada
        co2_input_layout = QHBoxLayout()
        self.co2_min = QLineEdit(str(self.node.co2_min) if hasattr(self.node, 'co2_min') else "0,0")
        self.co2_max = QLineEdit(str(self.node.co2_max) if hasattr(self.node, 'co2_max') else "0,0")
        
        validator = self.quantity.validator()
        for field in [self.co2_min, self.co2_max]:
            field.setValidator(validator)
            field.textEdited.connect(lambda text, f=field: f.setPlaceholderText("") if text else f.setPlaceholderText(
                f"Límite CO2 {'inferior' if f == self.co2_min else 'superior'} (ton)"))
        
        co2_input_layout.addWidget(self.co2_min)
        co2_input_layout.addWidget(self.co2_max)
        self.form_layout.addRow(co2_input_layout)
    
    def setup_investment_section(self):
        """Configura la sección de inversión"""
        # Límites de inversión
        inv_limits_label_layout = QHBoxLayout()
        inv_limits_label_layout.addWidget(QLabel("Límite inferior de inversión (USD)"))
        inv_limits_label_layout.addWidget(QLabel("Límite superior de inversión (USD)"))
        self.form_layout.addRow(inv_limits_label_layout)
        
        inv_limits_input_layout = QHBoxLayout()
        self.inv_min = QLineEdit(str(self.node.inv_min) if hasattr(self.node, 'inv_min') else "0,0")
        self.inv_max = QLineEdit(str(self.node.inv_max) if hasattr(self.node, 'inv_max') else "0,0")
        
        validator = self.quantity.validator()
        for field in [self.inv_min, self.inv_max]:
            field.setValidator(validator)
            field.textEdited.connect(lambda text, f=field: f.setPlaceholderText("") if text else f.setPlaceholderText(
                "Límite inversión inferior (USD)" if f == self.inv_min else 
                "Límite inversión superior (USD)"))
        
        inv_limits_input_layout.addWidget(self.inv_min)
        inv_limits_input_layout.addWidget(self.inv_max)
        self.form_layout.addRow(inv_limits_input_layout)
        
        # Inversión individual
        inv_layout = QHBoxLayout()
        inv_layout.addWidget(QLabel("Inversión (USD):"))
        self.inversion = QLineEdit(str(self.node.inversion) if hasattr(self.node, 'inversion') else "0,0")
        self.inversion.setValidator(validator)
        self.inversion.textEdited.connect(lambda text, f=self.inversion: f.setPlaceholderText("") if text else f.setPlaceholderText("Inversión (USD)"))
        inv_layout.addWidget(self.inversion)
        self.form_layout.addRow(inv_layout)
    
    def setup_description_field(self):
        """Configura el campo de descripción"""
        self.desc_input = QTextEdit(self.node.description)
        self.desc_input.setMaximumHeight(80)
        self.layout.addWidget(QLabel("Descripción:"))
        self.layout.addWidget(self.desc_input)
    
    def setup_action_buttons(self):
        """Configura los botones de acción"""
        self.button_box = QHBoxLayout()
        self.save_btn = QPushButton("Guardar")
        self.cancel_btn = QPushButton("Cancelar")
        self.button_box.addWidget(self.save_btn)
        self.button_box.addWidget(self.cancel_btn)
        self.layout.addLayout(self.button_box)
        
        self.save_btn.clicked.connect(self.accept_changes)
        self.cancel_btn.clicked.connect(self.reject)
    
    def accept_changes(self):
        """Valida y guarda los cambios realizados en el nodo"""
        new_name = self.name_input.text()
        if new_name != self.node.name and new_name in self.parent.view.used_names:
            QMessageBox.warning(self, "Nombre duplicado", 
                              "Ya existe un nodo con este nombre. Por favor elija otro.")
            return
        
        # Actualiza las propiedades del nodo
        self.update_node_properties(new_name)
        self.accept()
    
    def update_node_properties(self, new_name):
        """Actualiza las propiedades del nodo con los valores del diálogo"""
        def parse_float(value):
            return float(value.replace(',', '.')) if value else 0.0
        
        self.node.name = new_name
        self.node.energy_type = self.energy_type.currentText()
        self.node.quantity = parse_float(self.quantity.text())
        self.node.co2_min = parse_float(self.co2_min.text())
        self.node.co2_max = parse_float(self.co2_max.text())
        self.node.inv_min = parse_float(self.inv_min.text())
        self.node.inv_max = parse_float(self.inv_max.text())
        self.node.inversion = parse_float(self.inversion.text())
        self.node.description = self.desc_input.toPlainText()
        self.node.update_text_item()

class SpecialNode(QGraphicsEllipseItem):
    """Nodo especial (starter o end) que no se puede editar ni eliminar pero puede moverse y conectarse"""
    def __init__(self, x, y, name, radius=30):
        super().__init__(0, 0, radius * 2, radius * 2)
        self.setPos(x - radius, y - radius)
        self.setBrush(QBrush(QColor(0, 200, 0) if name == "starter" else QColor(200, 0, 0)))
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.OpenHandCursor)
        
        self.radius = radius
        self.center = QPointF(x, y)
        self.name = name
        self.is_special = True
        
        self.text_item = QGraphicsTextItem(self.name, self)
        self.text_item.setPos(radius - self.text_item.boundingRect().width()/2, 
                             radius - self.text_item.boundingRect().height()/2)
        self.text_item.setDefaultTextColor(Qt.black)
        
        self.arrows = []
    
    def add_arrow(self, arrow):
        """Añade una flecha conectada a este nodo"""
        self.arrows.append(arrow)

    def remove_arrow(self, arrow):
        """Elimina una flecha conectada a este nodo"""
        if arrow in self.arrows:
            self.arrows.remove(arrow)

    def itemChange(self, change, value):
        """Actualiza la posición de las flechas cuando se mueve el nodo"""
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            self.center = self.pos() + QPointF(self.radius, self.radius)
            for arrow in self.arrows:
                arrow.update_position()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """Los nodos especiales no tienen diálogo de edición"""
        super().mouseDoubleClickEvent(event)

class Node(QGraphicsEllipseItem):
    """Nodo normal que puede ser editado y eliminado"""
    _next_id = 1  # Contador para nombres automáticos
    
    def __init__(self, x, y, radius=30):
        super().__init__(0, 0, radius * 2, radius * 2)
        self.setPos(x - radius, y - radius)
        self.setBrush(QBrush(QColor(100, 100, 255)))
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.OpenHandCursor)
        
        self.radius = radius
        self.center = QPointF(x, y)
        self.name = f"Instancia {Node._next_id}"
        Node._next_id += 1
        self.energy_type = "Electricidad (kWh)"
        self.quantity = 0.0
        self.co2_min = 0.0
        self.co2_max = 0.0
        self.inv_min = 0.0
        self.inv_max = 0.0
        self.inversion = 0.0
        self.description = ""
        self.is_special = False
        
        self.text_item = QGraphicsTextItem(self.name, self)
        self.text_item.setPos(radius - self.text_item.boundingRect().width()/2, 
                             radius - self.text_item.boundingRect().height()/2)
        self.text_item.setDefaultTextColor(Qt.black)
        
        self.arrows = []
    
    def update_properties(self, dialog):
        """Actualiza las propiedades desde el diálogo"""
        self.name = dialog.name_input.text()
        self.energy_type = dialog.energy_type.currentText()
        self.quantity = dialog.node.quantity
        self.co2_min = dialog.node.co2_min
        self.co2_max = dialog.node.co2_max
        self.inv_min = dialog.node.inv_min
        self.inv_max = dialog.node.inv_max
        self.inversion = dialog.node.inversion
        self.description = dialog.desc_input.toPlainText()
        self.update_text_item()
    
    def update_text_item(self):
        """Actualiza el texto mostrado en el nodo"""
        self.text_item.setPlainText(self.name)
        self.text_item.setPos(self.radius - self.text_item.boundingRect().width()/2, 
                            self.radius - self.text_item.boundingRect().height()/2)
    
    def add_arrow(self, arrow):
        """Añade una flecha conectada a este nodo"""
        self.arrows.append(arrow)

    def remove_arrow(self, arrow):
        """Elimina una flecha conectada a este nodo"""
        if arrow in self.arrows:
            self.arrows.remove(arrow)

    def itemChange(self, change, value):
        """Actualiza la posición de las flechas cuando se mueve el nodo"""
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            self.center = self.pos() + QPointF(self.radius, self.radius)
            for arrow in self.arrows:
                arrow.update_position()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """Abre el diálogo de edición al hacer doble clic"""
        if event.button() == Qt.LeftButton:
            view = self.scene().views()[0]
            if not any([view.deleting_node, view.deleting_arrow, view.creating_arrow]):
                dialog = NodeDialog(self, view)
                if dialog.exec() == QDialog.Accepted:
                    self.update_properties(dialog)
        super().mouseDoubleClickEvent(event)

class Arrow(QGraphicsPathItem):
    """Flecha que conecta dos nodos"""
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.arrow_size = 12
        self.setZValue(-1)
        self.setPen(QPen(Qt.black, 2))
        
        self.start_node.add_arrow(self)
        self.end_node.add_arrow(self)
        
        self.update_position()
    
    def update_position(self):
        """Actualiza la posición de la flecha cuando se mueven los nodos"""
        if not self.start_node or not self.end_node:
            return

        line = QLineF(self.start_node.center, self.end_node.center)

        if line.length() == 0:
            return

        angle = math.atan2(line.dy(), line.dx())
        
        start_point = self.start_node.center + QPointF(
            math.cos(angle) * self.start_node.radius,
            math.sin(angle) * self.start_node.radius
        )
        end_point = self.end_node.center - QPointF(
            math.cos(angle) * self.end_node.radius,
            math.sin(angle) * self.end_node.radius
        )

        path = QPainterPath()
        path.moveTo(start_point)
        path.lineTo(end_point)

        arrow_head = QPolygonF()
        arrow_head.append(end_point)
        
        arrow_point1 = end_point - QPointF(
            math.cos(angle + math.pi/6) * self.arrow_size,
            math.sin(angle + math.pi/6) * self.arrow_size
        )
        arrow_point2 = end_point - QPointF(
            math.cos(angle - math.pi/6) * self.arrow_size,
            math.sin(angle - math.pi/6) * self.arrow_size
        )
        
        arrow_head.append(arrow_point1)
        arrow_head.append(arrow_point2)
        arrow_head.append(end_point)

        path.addPolygon(arrow_head)
        self.setPath(path)

    def remove(self):
        """Elimina la flecha de los nodos y de la escena"""
        self.start_node.remove_arrow(self)
        self.end_node.remove_arrow(self)
        if self.scene():
            self.scene().removeItem(self)

class GraphEditor(QGraphicsView):
    """Vista principal del editor de grafos"""
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.setInteractive(True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.nodes = []
        self.arrows = []
        self.used_names = set()
        self._creating_arrow = False
        self._deleting_arrow = False
        self._deleting_node = False
        self.start_node = None
        
        # Crear nodos iniciales
        self.create_initial_nodes()
    
    def create_initial_nodes(self):
        """Crea los nodos iniciales (starter y end)"""
        # Nodo starter (verde)
        starter = SpecialNode(100, 100, "starter")
        self.scene().addItem(starter)
        self.nodes.append(starter)
        self.used_names.add(starter.name)
        
        # Nodo end (rojo)
        end = SpecialNode(300, 100, "end")
        self.scene().addItem(end)
        self.nodes.append(end)
        self.used_names.add(end.name)
    
    @property
    def creating_arrow(self):
        return self._creating_arrow
    
    @creating_arrow.setter
    def creating_arrow(self, value):
        self._creating_arrow = value
        if not value:
            if self.start_node:
                self.start_node.setSelected(False)
            self.start_node = None
    
    @property
    def deleting_arrow(self): return self._deleting_arrow
    
    @deleting_arrow.setter
    def deleting_arrow(self, value):
        self._deleting_arrow = value
        self._deleting_node = False
        self._creating_arrow = False
    
    @property
    def deleting_node(self): return self._deleting_node
    
    @deleting_node.setter
    def deleting_node(self, value):
        self._deleting_node = value
        self._deleting_arrow = False
        self._creating_arrow = False
    
    def check_reverse_connection(self, start, end):
        """Verifica si ya existe una conexión en dirección opuesta"""
        for arrow in self.arrows:
            if arrow.start_node == end and arrow.end_node == start:
                return True
        return False
    
    def mousePressEvent(self, event):
        """Maneja los eventos de clic del mouse"""
        pos = self.mapToScene(event.position().toPoint())
        items = self.scene().items(pos)
        
        if event.button() == Qt.LeftButton:
            if not items and (self.creating_arrow or self.deleting_arrow or self.deleting_node):
                self.creating_arrow = False
                self.deleting_arrow = False
                self.deleting_node = False
                self.update_toolbar_states()
                return
            
            if self.creating_arrow:
                self.handle_arrow_creation(items)
            elif self.deleting_arrow:
                self.handle_arrow_deletion(items)
            elif self.deleting_node:
                self.handle_node_deletion(items)
            else:
                super().mousePressEvent(event)
    
    def handle_arrow_creation(self, items):
        """Maneja la creación de flechas entre nodos con restricciones"""
        for item in items:
            if isinstance(item, (Node, SpecialNode)):
                if not self.start_node:
                    # Bloquear conexiones desde el nodo end
                    if item.name == "end":
                        QMessageBox.warning(self, "Conexión no permitida",
                                        "No se puede crear conexiones desde el nodo final.")
                        return
                    self.start_node = item
                    item.setSelected(True)
                else:
                    # Bloquear conexiones hacia el nodo starter
                    if item.name == "starter":
                        QMessageBox.warning(self, "Conexión no permitida",
                                        "No se puede crear conexiones hacia el nodo inicial.")
                        return
                    
                    # Bloquear conexión directa entre starter y end en cualquier dirección
                    if (self.start_node.name == "starter" and item.name == "end") or \
                    (self.start_node.name == "end" and item.name == "starter"):
                        QMessageBox.warning(self, "Conexión no permitida",
                                        "No se puede conectar el nodo inicial directamente con el nodo final.")
                        self.start_node.setSelected(False)
                        self.creating_arrow = False
                        self.update_toolbar_states()
                        return
                    
                    # Verificar conexión inversa existente
                    if self.check_reverse_connection(self.start_node, item):
                        QMessageBox.warning(self, "Conexión duplicada",
                                        "Ya existe una conexión en dirección opuesta.")
                        return
                    
                    # Verificar conexión directa existente
                    for arrow in self.arrows:
                        if arrow.start_node == self.start_node and arrow.end_node == item:
                            QMessageBox.warning(self, "Conexión existente",
                                            "Ya existe una conexión entre estos nodos.")
                            return
                    
                    new_arrow = Arrow(self.start_node, item)
                    self.scene().addItem(new_arrow)
                    self.arrows.append(new_arrow)
                
                    self.start_node.setSelected(False)
                    self.creating_arrow = False
                    self.update_toolbar_states()
                return

        if self.start_node:
            self.start_node.setSelected(False)
            self.creating_arrow = False
            self.update_toolbar_states()
    
    def handle_arrow_deletion(self, items):
        """Maneja la eliminación de flechas"""
        for item in items:
            if isinstance(item, Arrow):
                item.remove()
                if item in self.arrows:
                    self.arrows.remove(item)
                return
        
        self.deleting_arrow = False
        self.update_toolbar_states()
    
    def handle_node_deletion(self, items):
        """Maneja la eliminación de nodos (excepto los especiales)"""
        for item in items:
            if isinstance(item, Node) and not getattr(item, 'is_special', False):
                if item.name in self.used_names:
                    self.used_names.remove(item.name)
                
                arrows_to_remove = [arrow for arrow in self.arrows 
                                  if arrow.start_node == item or arrow.end_node == item]
                
                for arrow in arrows_to_remove:
                    arrow.remove()
                    if arrow in self.arrows:
                        self.arrows.remove(arrow)
                
                self.scene().removeItem(item)
                if item in self.nodes:
                    self.nodes.remove(item)
                return
        
        self.deleting_node = False
        self.update_toolbar_states()
    
    def create_node(self, x, y):
        """Crea un nuevo nodo normal en la posición especificada"""
        node = Node(x, y)
        self.scene().addItem(node)
        self.nodes.append(node)
        self.used_names.add(node.name)
        return node
    
    def update_toolbar_states(self):
        """Actualiza el estado de los botones en la barra de herramientas"""
        if hasattr(self, 'main_window'):
            self.main_window.update_toolbar_states()
    
    def get_graph_representation(self):
        """Devuelve la estructura del grafo en formato diccionario"""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # Recoger datos de los nodos
        for node in self.nodes:
            node_data = {
                "name": node.name,
                "type": "special" if node.is_special else "normal",
                "energy_type": getattr(node, 'energy_type', 'N/A'),
                "quantity": getattr(node, 'quantity', 0.0),
                "co2_limits": [getattr(node, 'co2_min', 0.0), 
                              getattr(node, 'co2_max', 0.0)],
                "inv_limits": [getattr(node, 'inv_min', 0.0), 
                              getattr(node, 'inv_max', 0.0)],
                "position": (node.center.x(), node.center.y())
            }
            graph["nodes"].append(node_data)
        
        # Recoger datos de las conexiones
        for arrow in self.arrows:
            edge_data = {
                "source": arrow.start_node.name,
                "target": arrow.end_node.name,
                "direction": "unidirectional"
            }
            graph["edges"].append(edge_data)
            
        return graph

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camaleon PSV Pro")
        self.setMinimumSize(800, 600)
        
        # Configuración de la escena
        self.setup_scene()
        
        # Configuración de la interfaz
        self.setup_ui()
        
        self.resize(800, 600)
    
    def setup_scene(self):
        """Configura la escena gráfica"""
        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        
        self.view = GraphEditor(self.scene)
        self.view.main_window = self
        self.scene.arrows = self.view.arrows
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setCentralWidget(central_widget)
        
        self.setup_toolbar()
    
    def setup_toolbar(self):
        """Configura la barra de herramientas"""
        self.toolbar = QToolBar("Herramientas principales")
        self.addToolBar(self.toolbar)
        
        self.toolbar.setStyleSheet("""
            QToolButton:checked {
                background-color: #0078d7;
                color: white;
                border: 1px solid #005499;
            }
            QToolButton:hover {
                background-color: #e5f1fb;
            }
        """)
        
        # Crear acciones
        self.create_actions()
        
        # Agregar acciones a la barra de herramientas
        self.toolbar.addActions([
            self.add_node_action,
            self.remove_node_action,
            self.remove_arrow_action,
            self.create_arrow_action,
            self.run_model_action
        ])
    
    def create_actions(self):
        """Crea las acciones para la barra de herramientas"""
        self.add_node_action = self.create_action("Agregar instancia", "Agregar nuevo nodo", self.add_node)
        self.remove_node_action = self.create_action("Eliminar instancia", "Eliminar nodo", self.toggle_remove_node, checkable=True)
        self.remove_arrow_action = self.create_action("Eliminar Flecha", "Eliminar flecha", self.toggle_remove_arrow, checkable=True)
        self.create_arrow_action = self.create_action("Crear Flecha", "Crear flecha entre nodos", self.toggle_create_arrow, checkable=True)
        self.run_model_action = self.create_action("Ejecutar Modelo", "Ejecutar el modelo de optimización", self.run_model)
    
    def create_action(self, text, tooltip, callback, checkable=False):
        """Crea una acción con los parámetros dados"""
        action = QAction(text, self)
        action.setToolTip(tooltip)
        action.triggered.connect(callback)
        action.setCheckable(checkable)
        return action
    
    def update_toolbar_states(self):
        """Actualiza el estado visual de los botones de la barra de herramientas"""
        self.remove_node_action.setChecked(self.view.deleting_node)
        self.remove_arrow_action.setChecked(self.view.deleting_arrow)
        self.create_arrow_action.setChecked(self.view.creating_arrow)
        
        for action in [self.remove_node_action, self.remove_arrow_action, self.create_arrow_action]:
            if action.isChecked():
                action.setText(f"> {action.text().replace('> ', '')}")
            else:
                action.setText(action.text().replace("> ", ""))
    
    def add_node(self):
        """Agrega un nuevo nodo normal"""
        self.view.deleting_node = False
        self.view.deleting_arrow = False
        self.view.creating_arrow = False
        self.update_toolbar_states()
        
        center = self.view.viewport().rect().center()
        scene_pos = self.view.mapToScene(center)
        self.view.create_node(scene_pos.x(), scene_pos.y())
    
    def toggle_remove_node(self):
        """Alterna el modo de eliminación de nodos"""
        self.view.deleting_node = not self.view.deleting_node
        self.update_toolbar_states()
    
    def toggle_remove_arrow(self):
        """Alterna el modo de eliminación de flechas"""
        self.view.deleting_arrow = not self.view.deleting_arrow
        self.update_toolbar_states()
    
    def toggle_create_arrow(self):
        """Alterna el modo de creación de flechas"""
        self.view.creating_arrow = not self.view.creating_arrow
        self.update_toolbar_states()
    
    
    def get_current_graph(self):
        """Devuelve la representación del grafo actual"""
        return self.view.get_graph_representation()
    
    def resizeEvent(self, event):
        """Ajusta el tamaño de la escena cuando se redimensiona la ventana"""
        size = event.size()
        self.view.setSceneRect(QRectF(QPointF(0.0, 0.0), 
                              QPointF(float(size.width()), float(size.height()))))
        super().resizeEvent(event)

    def run_model(self):
        """Ejecuta el modelo de optimización con el grafo actual"""
        graph_data = self.get_current_graph()
        
        # Procesar datos
        data_processor = backend.Data(graph_data)
        ranking = data_processor.get_ranking()
        
        # Mostrar resultados
        self.show_model_results(ranking)
    
    def show_model_results(self, ranking):
        """Muestra los resultados del modelo en un cuadro de diálogo"""
        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Ranking de Caminos")
        result_dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        title = QLabel("Top 5 Caminos con Menores Emisiones:")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        if not ranking:
            layout.addWidget(QLabel("No se encontraron caminos válidos"))
        else:
            for i, path_info in enumerate(ranking, 1):
                path_str = " → ".join(path_info['path'])
                emissions = f"{path_info['total_emissions']:.2f} kg CO2"
                text = f"{i}. {path_str} - {emissions}"
                layout.addWidget(QLabel(text))
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(result_dialog.close)
        layout.addWidget(close_btn)
        
        result_dialog.setLayout(layout)
        result_dialog.exec()

    def show_model_results(self, ranking):
        """Muestra los resultados del modelo en un cuadro de diálogo"""
        result_dialog = QDialog(self)
        result_dialog.setWindowTitle("Ranking de Caminos")
        result_dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Botón de exportación
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("Exportar a Excel")
        export_btn.clicked.connect(lambda: self.export_results(ranking))
        btn_layout.addWidget(export_btn)
        
        # Botón de cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(result_dialog.close)
        btn_layout.addWidget(close_btn)
        
        # Listado de resultados
        title = QLabel("Top 5 Caminos con Menores Emisiones:")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        if not ranking:
            layout.addWidget(QLabel("No se encontraron caminos válidos"))
        else:
            for i, path_info in enumerate(ranking, 1):
                path_str = " → ".join(path_info['path'])
                emissions = f"{path_info['total_emissions']:.2f} ton CO2"
                text = f"{i}. {path_str} - {emissions}"
                layout.addWidget(QLabel(text))
        
        layout.addLayout(btn_layout)
        result_dialog.setLayout(layout)
        result_dialog.exec()
    
    def export_results(self, ranking):
        """Maneja la exportación a Excel"""
        if not ranking:
            QMessageBox.warning(self, "Error", "No hay datos para exportar")
            return
        
        # Obtener nombre de archivo
        default_name = f"Resultados_Camaleon_PSV_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar resultados",
            os.path.join(os.path.expanduser("~"), "Documents", default_name),
            "Excel Files (*.xlsx)"
        )
        
        if filename:
            data_processor = backend.Data(self.get_current_graph())
            if data_processor.export_to_excel(ranking, filename):
                QMessageBox.information(self, "Éxito", f"Archivo guardado en:\n{filename}")
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar el archivo")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Configuración inicial de la aplicación
    app.setStyle('Fusion')
    palette = app.palette()
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    app.setPalette(palette)
    
    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()
    sys.exit(app.exec())