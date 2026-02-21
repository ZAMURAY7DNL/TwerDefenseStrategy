# Inspector de Desarrollo - Tactical Defense

Herramienta visual para editar valores del juego sin tocar código.

## 🚀 Cómo Usar

### Opción 1: Doble click (Windows)
```
dev_tools/run_inspector.bat
```

### Opción 2: Consola
```bash
# Desde el directorio raíz del proyecto
python dev_tools/inspector.py

# O como módulo
python -m dev_tools.inspector
```

## 📋 Qué Puede Editar

### ✅ Valores Soportados
- **Stats de unidades**: HP, ATK, Rango, Velocidad
- **Stats del héroe**: AP máximo, recuperación
- **Constantes**: FPS, tamaños, colores (numéricos)

### ❌ No Soportado (aún)
- Strings/textos
- Listas y diccionarios complejos
- Lógica de comportamiento
- Assets gráficos/sonidos

## 🔄 Auto-Refresh

El inspector detecta cambios en archivos cada 5 segundos. Si editas un archivo manualmente mientras el inspector está abierto, te avisará para que recargues.

## 💾 Guardar Cambios

1. Modifica los valores en los campos
2. Los valores modificados muestran ⏳
3. Click en "Guardar Cambios"
4. Se crea un archivo `.backup` automáticamente
5. **Reinicia el juego** para ver los cambios

## ⚠️ Importante

- Siempre se crea backup antes de guardar
- Valores no numéricos pueden no funcionar correctamente
- El juego debe reiniciarse para cargar cambios (no es hot-reload)

## 🐛 Troubleshooting

### No aparecen las clases
- Verifica que los archivos estén en `entities/`, `config/`, etc.
- Los valores deben ser asignaciones directas: `health = 100`

### Error al guardar
- Revisa que no tengas el archivo abierto en otro editor
- Verifica permisos de escritura
- Revisa el log en la pestaña "Log"

### Cambios no aparecen en el juego
- Recuerda: debes **reiniciar el juego**
- Verifica que guardaste (status debe decir "X cambios guardados")

## 📝 Estructura

```
dev_tools/
├── inspector.py       # UI principal (tkinter)
├── parser.py          # Parser de Python (AST)
├── file_monitor.py    # Monitoreo de archivos
├── __init__.py
├── README.md
└── run_inspector.bat  # Launcher Windows
```

## 🔧 Para Desarrolladores

Si quieres extender el inspector:

1. **Agregar soporte para nuevos tipos**: Modifica `_extract_value()` en `parser.py`
2. **Nueva UI**: Edita `setup_ui()` en `inspector.py`
3. **Más archivos**: Agrega patrones en `refresh_data()`
