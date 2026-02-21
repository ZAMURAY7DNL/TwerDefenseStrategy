"""
Tactical Defense - Inspector de Desarrollo
==========================================
Herramienta visual para editar valores del juego en tiempo real.
Usa tkinter para la interfaz y AST para parsear Python.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
import json

# Agregar parent al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dev_tools.parser import PythonCodeParser
from dev_tools.file_monitor import FileMonitor


class ValueEditor:
    """Widget para editar un valor individual."""
    def __init__(self, parent, name: str, value, on_change_callback):
        self.name = name
        self.original_value = value
        self.current_value = value
        self.on_change = on_change_callback
        self.modified = False
        
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='x', padx=5, pady=2)
        
        # Label del nombre
        self.label = ttk.Label(self.frame, text=f"{name}:", width=20, anchor='w')
        self.label.pack(side='left')
        
        # Entry para el valor
        self.var = tk.StringVar(value=str(value))
        self.entry = ttk.Entry(self.frame, textvariable=self.var, width=15)
        self.entry.pack(side='left', padx=5)
        
        # Indicador de modificación
        self.status_label = ttk.Label(self.frame, text="✓", foreground='green', width=3)
        self.status_label.pack(side='left')
        
        # Bind cambios
        self.var.trace('w', self._on_value_changed)
    
    def _on_value_changed(self, *args):
        """Callback cuando cambia el valor."""
        try:
            new_val = self.var.get()
            
            # Intentar convertir al tipo original
            if isinstance(self.original_value, int):
                new_val = int(new_val)
            elif isinstance(self.original_value, float):
                new_val = float(new_val)
            
            self.current_value = new_val
            self.modified = (new_val != self.original_value)
            
            if self.modified:
                self.status_label.config(text="⏳", foreground='orange')
            else:
                self.status_label.config(text="✓", foreground='green')
            
            if self.on_change:
                self.on_change(self.name, new_val)
                
        except ValueError:
            self.status_label.config(text="✗", foreground='red')
    
    def get_value(self):
        """Retorna el valor actual."""
        try:
            if isinstance(self.original_value, int):
                return int(self.var.get())
            elif isinstance(self.original_value, float):
                return float(self.var.get())
            return self.var.get()
        except ValueError:
            return self.original_value
    
    def reset(self):
        """Resetea al valor original."""
        self.var.set(str(self.original_value))
        self.modified = False
        self.status_label.config(text="✓", foreground='green')


class ClassEditor:
    """Editor para una clase con múltiples atributos."""
    def __init__(self, parent, class_name: str, class_info: dict, file_path: str):
        self.class_name = class_name
        self.file_path = file_path
        self.attributes = class_info.get('attributes', {})
        self.editors = {}
        self.modified_values = {}
        
        # Frame contenedor con borde
        self.frame = ttk.LabelFrame(parent, text=f"📦 {class_name}", padding=10)
        self.frame.pack(fill='x', padx=5, pady=5)
        
        # Crear editores para cada atributo
        for attr_name, attr_value in self.attributes.items():
            if isinstance(attr_value, (int, float)):
                editor = ValueEditor(
                    self.frame, 
                    attr_name, 
                    attr_value,
                    lambda n, v, cn=class_name: self._on_attribute_change(cn, n, v)
                )
                self.editors[attr_name] = editor
        
        # Botones
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(btn_frame, text="Reset", command=self.reset_all).pack(side='left', padx=2)
    
    def _on_attribute_change(self, class_name: str, attr_name: str, value):
        """Callback cuando cambia un atributo."""
        self.modified_values[attr_name] = value
    
    def get_modified_values(self) -> dict:
        """Retorna solo los valores modificados."""
        return self.modified_values
    
    def reset_all(self):
        """Resetea todos los valores."""
        for editor in self.editors.values():
            editor.reset()
        self.modified_values.clear()
    
    def update_values(self, new_attributes: dict):
        """Actualiza los valores desde el parser (recarga)."""
        for attr_name, new_value in new_attributes.items():
            if attr_name in self.editors:
                editor = self.editors[attr_name]
                if not editor.modified:  # Solo si no está siendo editado
                    editor.original_value = new_value
                    editor.var.set(str(new_value))


class InspectorApp:
    """Aplicación principal del Inspector."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tactical Defense - Inspector de Desarrollo")
        self.root.geometry("900x700")
        self.root.minsize(600, 400)
        
        # Detectar directorio del proyecto
        self.project_root = Path(__file__).parent.parent
        
        # Parser y monitor
        self.parser = PythonCodeParser(str(self.project_root))
        self.monitor = FileMonitor(str(self.project_root), check_interval=5.0)
        self.monitor.on_change = self._on_files_changed
        
        # UI
        self.class_editors = {}
        self.setup_ui()
        
        # Cargar datos iniciales
        self.refresh_data()
        
        # Iniciar monitoreo
        self.monitor.set_patterns([
            'entities/*.py',
            'config/*.py',
            'systems/*.py',
            'core/*.py'
        ])
        self.monitor.start()
        
        # Auto-refresh de UI
        self.schedule_ui_refresh()
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # ===== HEADER =====
        header = ttk.Frame(main_frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(1, weight=1)
        
        ttk.Label(header, text="🔧 Inspector", font=('Arial', 16, 'bold')).grid(row=0, column=0, sticky='w')
        
        # Botones de acción
        btn_frame = ttk.Frame(header)
        btn_frame.grid(row=0, column=2, sticky='e')
        
        ttk.Button(btn_frame, text="🔄 Recargar", command=self.refresh_data).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="💾 Guardar Cambios", command=self.save_changes).pack(side='left', padx=2)
        
        # Status
        self.status_var = tk.StringVar(value="Listo")
        self.status_label = ttk.Label(header, textvariable=self.status_var, foreground='gray')
        self.status_label.grid(row=1, column=0, columnspan=3, sticky='w', pady=(5, 0))
        
        # ===== NOTEBOOK (Pestañas) =====
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        
        # Pestaña: Entidades
        self.tab_entities = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_entities, text="Entidades")
        self.setup_entities_tab()
        
        # Pestaña: Configuración
        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="Configuración")
        self.setup_config_tab()
        
        # Pestaña: Log
        self.tab_log = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log, text="Log")
        self.setup_log_tab()
        
        # ===== FOOTER =====
        footer = ttk.Frame(main_frame)
        footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.last_update_var = tk.StringVar(value="Última actualización: Nunca")
        ttk.Label(footer, textvariable=self.last_update_var, foreground='gray').pack(side='left')
        
        ttk.Label(footer, text="Auto-refresh: 5s", foreground='gray').pack(side='right')
    
    def setup_entities_tab(self):
        """Configura la pestaña de entidades."""
        # Canvas con scrollbar para muchas clases
        canvas = tk.Canvas(self.tab_entities)
        scrollbar = ttk.Scrollbar(self.tab_entities, orient="vertical", command=canvas.yview)
        self.entities_frame = ttk.Frame(canvas)
        
        self.entities_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.entities_frame, anchor="nw", width=850)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Label inicial
        ttk.Label(self.entities_frame, text="Cargando entidades...", foreground='gray').pack(pady=20)
    
    def setup_config_tab(self):
        """Configura la pestaña de configuración."""
        self.config_frame = ttk.Frame(self.tab_config, padding=10)
        self.config_frame.pack(fill='both', expand=True)
        
        ttk.Label(self.config_frame, text="Constantes del juego:", font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.config_container = ttk.Frame(self.config_frame)
        self.config_container.pack(fill='both', expand=True)
        
        ttk.Label(self.config_frame, text="(Se muestran valores de constants.py)", foreground='gray').pack(anchor='w', pady=(10, 0))
    
    def setup_log_tab(self):
        """Configura la pestaña de log."""
        self.log_text = scrolledtext.ScrolledText(self.tab_log, wrap=tk.WORD, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(self.tab_log)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_log).pack(side='right')
    
    def log(self, message: str):
        """Agrega mensaje al log."""
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.log_text.configure(state='disabled')
    
    def clear_log(self):
        """Limpia el log."""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, 'end')
        self.log_text.configure(state='disabled')
    
    def refresh_data(self):
        """Recarga los datos del proyecto."""
        self.status_var.set("🔄 Escaneando archivos...")
        self.root.update()
        
        # Escanear
        self.parser.scan_project()
        values = self.parser.get_editable_values()
        
        # Limpiar frames
        for widget in self.entities_frame.winfo_children():
            widget.destroy()
        
        for widget in self.config_container.winfo_children():
            widget.destroy()
        
        self.class_editors.clear()
        
        # Crear editores
        for file_path, file_data in values.items():
            # Separador por archivo
            file_label = ttk.Label(self.entities_frame, text=f"📁 {file_path}", 
                                   font=('Arial', 10, 'bold'), foreground='blue')
            file_label.pack(anchor='w', pady=(10, 5), padx=5)
            
            for class_name, class_info in file_data.items():
                if class_info['type'] == 'class':
                    editor = ClassEditor(
                        self.entities_frame,
                        class_name,
                        class_info,
                        file_path
                    )
                    key = f"{file_path}#{class_name}"
                    self.class_editors[key] = editor
        
        # Configuración
        config_data = values.get('config/constants.py', {})
        if '__constants__' in config_data:
            for const_name, const_value in config_data['__constants__'].get('values', {}).items():
                if isinstance(const_value, (int, float)):
                    editor = ValueEditor(
                        self.config_container,
                        const_name,
                        const_value,
                        lambda n, v: None  # No tracking para config aún
                    )
        
        self.status_var.set(f"✅ {len(self.class_editors)} clases cargadas")
        self.last_update_var.set("Última actualización: Ahora")
        self.log(f"Recarga completa: {len(self.class_editors)} clases encontradas")
    
    def save_changes(self):
        """Guarda los cambios a los archivos."""
        changes_count = 0
        errors = []
        
        for key, editor in self.class_editors.items():
            file_path, class_name = key.split('#', 1)
            modified = editor.get_modified_values()
            
            for attr_name, new_value in modified.items():
                success = self.parser.modify_value(file_path, class_name, attr_name, new_value)
                if success:
                    changes_count += 1
                    self.log(f"Guardado: {file_path} -> {class_name}.{attr_name} = {new_value}")
                else:
                    errors.append(f"{file_path}::{class_name}.{attr_name}")
        
        if changes_count > 0:
            self.status_var.set(f"💾 {changes_count} cambios guardados")
            messagebox.showinfo("Guardado", f"{changes_count} valores modificados.\n\n⚠️ Reinicia el juego para ver los cambios.")
        elif errors:
            self.status_var.set(f"❌ Errores al guardar")
            messagebox.showerror("Error", f"No se pudieron guardar algunos valores:\n" + "\n".join(errors))
        else:
            self.status_var.set("ℹ️ No hay cambios para guardar")
    
    def _on_files_changed(self, changed_files: list):
        """Callback cuando el monitor detecta cambios."""
        file_names = [Path(f).name for f in changed_files]
        self.log(f"Archivos modificados externamente: {', '.join(file_names)}")
        # Podríamos auto-recargar aquí, pero mejor notificar al usuario
        self.status_var.set(f"📝 Cambios externos detectados - Presiona Recargar")
    
    def schedule_ui_refresh(self):
        """Programa actualización periódica de la UI."""
        # Aquí podríamos actualizar indicadores visuales
        self.root.after(5000, self.schedule_ui_refresh)
    
    def on_closing(self):
        """Limpieza al cerrar."""
        self.monitor.stop()
        self.root.destroy()


def main():
    """Punto de entrada."""
    root = tk.Tk()
    app = InspectorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
