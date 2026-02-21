"""
File Monitor - Monitorea cambios en archivos
=============================================
Detecta modificaciones en archivos Python cada N segundos.
"""
import os
import time
import threading
from pathlib import Path
from typing import Callable, List, Dict


class FileMonitor:
    """Monitorea cambios en archivos del proyecto."""
    
    def __init__(self, project_root: str, check_interval: float = 5.0):
        self.project_root = Path(project_root)
        self.check_interval = check_interval
        self.file_mtimes: Dict[str, float] = {}
        self.patterns: List[str] = ['*.py']
        self.on_change: Optional[Callable] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._watched_files: set = set()
    
    def set_patterns(self, patterns: List[str]):
        """Establece patrones de archivos a monitorear."""
        self.patterns = patterns
        self._update_watched_files()
    
    def _update_watched_files(self):
        """Actualiza la lista de archivos a monitorear."""
        self._watched_files.clear()
        
        for pattern in self.patterns:
            # Si el patrón tiene directorio (ej: entities/*.py)
            if '/' in pattern:
                dir_part, file_part = pattern.rsplit('/', 1)
                target_dir = self.project_root / dir_part
                if target_dir.exists():
                    for f in target_dir.glob(file_part):
                        if f.is_file():
                            self._watched_files.add(str(f))
            else:
                # Patrón simple
                for f in self.project_root.rglob(pattern):
                    if f.is_file():
                        self._watched_files.add(str(f))
        
        # Inicializar mtimes
        for file_path in self._watched_files:
            try:
                mtime = os.path.getmtime(file_path)
                self.file_mtimes[file_path] = mtime
            except OSError:
                pass
    
    def check_changes(self) -> List[str]:
        """Verifica si hay cambios en los archivos monitoreados."""
        changed_files = []
        
        # Actualizar lista de archivos (por si se crearon nuevos)
        self._update_watched_files()
        
        for file_path in self._watched_files:
            try:
                current_mtime = os.path.getmtime(file_path)
                
                if file_path in self.file_mtimes:
                    if current_mtime > self.file_mtimes[file_path]:
                        changed_files.append(file_path)
                        self.file_mtimes[file_path] = current_mtime
                else:
                    # Archivo nuevo
                    self.file_mtimes[file_path] = current_mtime
                    
            except OSError:
                # Archivo eliminado?
                if file_path in self.file_mtimes:
                    del self.file_mtimes[file_path]
        
        return changed_files
    
    def _monitor_loop(self):
        """Loop de monitoreo en thread separado."""
        while self._running:
            changed = self.check_changes()
            if changed and self.on_change:
                try:
                    self.on_change(changed)
                except Exception as e:
                    print(f"[MONITOR ERROR] {e}")
            
            time.sleep(self.check_interval)
    
    def start(self):
        """Inicia el monitoreo en un thread separado."""
        if self._running:
            return
        
        self._running = True
        self._update_watched_files()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        print(f"[MONITOR] Iniciado (intervalo: {self.check_interval}s)")
    
    def stop(self):
        """Detiene el monitoreo."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        print("[MONITOR] Detenido")
    
    def force_check(self) -> List[str]:
        """Fuerza una verificación inmediata."""
        return self.check_changes()


if __name__ == '__main__':
    # Test
    def on_change(files):
        print(f"[CAMBIOS DETECTADOS] {len(files)} archivos:")
        for f in files:
            print(f"  - {f}")
    
    monitor = FileMonitor(r'c:\Users\user\Documents\liko', check_interval=2.0)
    monitor.set_patterns(['entities/*.py', 'config/*.py'])
    monitor.on_change = on_change
    
    print("Monitoreando por 10 segundos... Modifica algún archivo.")
    monitor.start()
    
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    
    monitor.stop()
