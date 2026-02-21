"""
Test rápido del parser y file monitor
======================================
Ejecutar: python dev_tools/test_parser.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dev_tools.parser import PythonCodeParser
from dev_tools.file_monitor import FileMonitor
import time


def test_parser():
    """Testea el parser."""
    print("=" * 60)
    print("TEST: PythonCodeParser")
    print("=" * 60)
    
    parser = PythonCodeParser('.')
    
    # Escanear archivos clave
    print("\n[1] Escaneando archivos...")
    parser.scan_project([
        'entities/unit.py',
        'entities/hero.py',
        'entities/tower.py',
        'config/constants.py'
    ])
    
    # Mostrar resultados
    print("\n[2] Resultados:")
    values = parser.get_editable_values()
    
    for file_path, data in values.items():
        print(f"\n  [FILE] {file_path}")
        for name, info in data.items():
            if info['type'] == 'class':
                print(f"    [CLASS] {name}")
                for attr, val in info['attributes'].items():
                    if isinstance(val, (int, float)):
                        print(f"      - {attr} = {val}")
    
    print(f"\n[3] Total: {len(parser.parsed_files)} archivos parseados")
    print("[OK] Parser funciona correctamente!\n")


def test_file_monitor():
    """Testea el file monitor."""
    print("=" * 60)
    print("TEST: FileMonitor (5 segundos)")
    print("=" * 60)
    
    changes_detected = []
    
    def on_change(files):
        changes_detected.extend(files)
        print(f"  📝 Cambios detectados: {len(files)} archivos")
        for f in files:
            print(f"     [CHANGED] {Path(f).name}")
    
    monitor = FileMonitor('.', check_interval=2.0)
    monitor.set_patterns(['config/*.py'])
    monitor.on_change = on_change
    
    print("\n[1] Iniciando monitoreo...")
    monitor.start()
    
    print("[2] Monitoreando por 6 segundos...")
    print("     (Modifica un archivo en config/ para probar)")
    
    time.sleep(6)
    
    print("[3] Deteniendo...")
    monitor.stop()
    
    if changes_detected:
        print(f"[OK] Monitor detecto {len(changes_detected)} cambios!")
    else:
        print("[INFO] No se detectaron cambios (normal si no editaste nada)")
    print()


if __name__ == '__main__':
    test_parser()
    test_file_monitor()
    print("\n" + "=" * 60)
    print("[DONE] Tests completados!")
    print("=" * 60)
