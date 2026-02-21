"""
Python Code Parser - Extrae información de archivos Python
===========================================================
Usa AST (Abstract Syntax Tree) para parsear código sin ejecutarlo.
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class ClassInfo:
    """Representa información de una clase Python."""
    def __init__(self, name: str, file_path: str, line_number: int):
        self.name = name
        self.file_path = file_path
        self.line_number = line_number
        self.attributes: Dict[str, Any] = {}  # nombre -> valor
        self.methods: List[str] = []
        self.docstring: Optional[str] = None


class ParsedFile:
    """Representa un archivo Python parseado."""
    def __init__(self, path: str):
        self.path = path
        self.classes: Dict[str, ClassInfo] = {}
        self.functions: List[str] = []
        self.constants: Dict[str, Any] = {}
        self.imports: List[str] = []
        self.last_modified: float = 0


class PythonCodeParser:
    """Parser de código Python usando AST."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.parsed_files: Dict[str, ParsedFile] = {}
    
    def parse_file(self, file_path: str) -> Optional[ParsedFile]:
        """Parsea un archivo Python y extrae información."""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            parsed = ParsedFile(file_path)
            parsed.last_modified = full_path.stat().st_mtime
            
            for node in ast.iter_child_nodes(tree):
                # Clases
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class(node, file_path)
                    parsed.classes[class_info.name] = class_info
                
                # Funciones
                elif isinstance(node, ast.FunctionDef):
                    parsed.functions.append(node.name)
                
                # Constantes (assignments a nivel de módulo)
                elif isinstance(node, ast.Assign):
                    self._extract_constant(node, parsed)
                
                # Imports
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._extract_import(node, parsed)
            
            self.parsed_files[file_path] = parsed
            return parsed
            
        except SyntaxError as e:
            print(f"[ERROR] Syntax error en {file_path}: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Error parseando {file_path}: {e}")
            return None
    
    def _extract_class(self, node: ast.ClassDef, file_path: str) -> ClassInfo:
        """Extrae información de una clase."""
        class_info = ClassInfo(
            name=node.name,
            file_path=file_path,
            line_number=node.lineno
        )
        
        # Docstring
        docstring = ast.get_docstring(node)
        if docstring:
            class_info.docstring = docstring.strip()
        
        for item in node.body:
            # Atributos de clase (assignments)
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        value = self._extract_value(item.value)
                        if value is not None:
                            class_info.attributes[target.id] = value
            
            # Métodos
            elif isinstance(item, ast.FunctionDef):
                class_info.methods.append(item.name)
                
                # Intentar extraer valores por defecto
                if item.name == '__init__':
                    self._extract_init_defaults(item, class_info)
        
        return class_info
    
    def _extract_init_defaults(self, node: ast.FunctionDef, class_info: ClassInfo):
        """Extrae valores por defecto del __init__."""
        # Buscar self.attr = value en el __init__
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            value = self._extract_value(item.value)
                            if value is not None:
                                class_info.attributes[target.attr] = value
    
    def _extract_value(self, node: ast.AST) -> Any:
        """Extrae valor literal de un nodo AST."""
        if isinstance(node, ast.Num):  # Python < 3.8
            return node.n
        elif isinstance(node, ast.Constant):  # Python >= 3.8
            return node.value
        elif isinstance(node, ast.Str):  # Python < 3.8
            return node.s
        elif isinstance(node, ast.NameConstant):  # True, False, None
            return node.value
        elif isinstance(node, ast.List):
            return [self._extract_value(e) for e in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._extract_value(e) for e in node.elts)
        elif isinstance(node, ast.Dict):
            return {self._extract_value(k): self._extract_value(v) 
                   for k, v in zip(node.keys, node.values)}
        return None
    
    def _extract_constant(self, node: ast.Assign, parsed: ParsedFile):
        """Extrae constantes a nivel de módulo."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Solo nombres en MAYÚSCULAS o con underscore
                if target.id.isupper() or '_' in target.id:
                    value = self._extract_value(node.value)
                    if value is not None:
                        parsed.constants[target.id] = value
    
    def _extract_import(self, node: ast.AST, parsed: ParsedFile):
        """Extrae información de imports."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                parsed.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                parsed.imports.append(f"{module}.{alias.name}")
    
    def get_editable_values(self) -> Dict[str, Dict]:
        """
        Obtiene todos los valores editables del proyecto.
        Retorna: {archivo: {clase/constante: {atributo: valor}}}
        """
        result = {}
        
        for file_path, parsed in self.parsed_files.items():
            file_data = {}
            
            # Clases con atributos numéricos
            for class_name, class_info in parsed.classes.items():
                numeric_attrs = {}
                for attr, value in class_info.attributes.items():
                    if isinstance(value, (int, float)):
                        numeric_attrs[attr] = value
                
                if numeric_attrs:
                    file_data[class_name] = {
                        'type': 'class',
                        'line': class_info.line_number,
                        'attributes': numeric_attrs
                    }
            
            # Constantes
            if parsed.constants:
                file_data['__constants__'] = {
                    'type': 'constants',
                    'values': {k: v for k, v in parsed.constants.items() 
                              if isinstance(v, (int, float, str))}
                }
            
            if file_data:
                result[file_path] = file_data
        
        return result
    
    def modify_value(self, file_path: str, class_name: str, 
                    attribute: str, new_value: Any) -> bool:
        """
        Modifica un valor en un archivo Python.
        Retorna True si tuvo éxito.
        """
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Encontrar la línea del atributo
            parsed = self.parsed_files.get(file_path)
            if not parsed:
                return False
            
            class_info = parsed.classes.get(class_name)
            if not class_info:
                return False
            
            # Buscar y reemplazar el valor
            modified = False
            new_lines = []
            
            for i, line in enumerate(lines, 1):
                # Patrón: atributo = valor (en cualquier parte de la línea)
                # O: self.atributo = valor
                patterns = [
                    rf'^\s*{re.escape(attribute)}\s*=\s*([^#\n]+)',
                    rf'^\s*self\.{re.escape(attribute)}\s*=\s*([^#\n]+)',
                ]
                
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        # Preservar indentación y comentarios
                        indent = len(line) - len(line.lstrip())
                        comment = ''
                        if '#' in line:
                            comment = ' #' + line.split('#', 1)[1].rstrip()
                        
                        new_line = ' ' * indent + f"{attribute} = {new_value}{comment}\n"
                        new_lines.append(new_line)
                        modified = True
                        break
                else:
                    new_lines.append(line)
            
            if modified:
                # Backup antes de guardar
                backup_path = str(full_path) + '.backup'
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                # Guardar cambios
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                # Re-parsear
                self.parse_file(file_path)
                return True
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Error modificando {file_path}: {e}")
            return False
    
    def scan_project(self, patterns: List[str] = None):
        """Escanea el proyecto buscando archivos Python."""
        if patterns is None:
            patterns = ['entities/*.py', 'config/*.py', 'systems/*.py', 'core/*.py']
        
        for pattern in patterns:
            for py_file in self.project_root.glob(pattern):
                if py_file.is_file() and py_file.suffix == '.py':
                    relative = str(py_file.relative_to(self.project_root))
                    self.parse_file(relative)


if __name__ == '__main__':
    # Test
    parser = PythonCodeParser(r'c:\Users\user\Documents\liko')
    parser.scan_project()
    
    values = parser.get_editable_values()
    for file, data in values.items():
        print(f"\n📁 {file}")
        for name, info in data.items():
            if info['type'] == 'class':
                print(f"  📦 {name}")
                for attr, val in info['attributes'].items():
                    print(f"    • {attr} = {val}")
            elif info['type'] == 'constants':
                print(f"  🔧 Constantes:")
                for const, val in info['values'].items():
                    print(f"    • {const} = {val}")
