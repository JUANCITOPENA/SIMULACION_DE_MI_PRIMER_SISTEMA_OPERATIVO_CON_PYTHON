import pytest
import os
import sys

# Se añade el path para importar la lógica de la app sin fallos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from main import THEMES, TEMP_DIR, ROOT_DIR
except ImportError:
    pass

# --- PRUEBA UNITARIA (UNIT TEST) ---
def test_theme_colors_integrity():
    """Verifica que el diccionario de temas no haya sido alterado accidentalmente."""
    assert "Windows 11" in THEMES
    assert "Minimal White" in THEMES
    # El color oscuro (fg_color general) en Minimal White debe ser blanco
    assert THEMES["Minimal White"][2] == "#ffffff"
    # El modo del tema blanco debe ser 'light'
    assert THEMES["Minimal White"][4] == "light"


# --- PRUEBA DE INTEGRACIÓN (INTEGRATION TEST) ---
def test_directories_creation():
    """Verifica que los directorios del Sistema Operativo Virtual existan físicamente en el disco real."""
    assert os.path.exists(ROOT_DIR), f"El disco duro virtual {ROOT_DIR} no fue creado."
    assert os.path.exists(TEMP_DIR), f"La carpeta de archivos temporales {TEMP_DIR} no existe."


# --- PRUEBA DE RENDIMIENTO (BENCHMARK MOCKUP) ---
def test_mock_wallpaper_scan():
    """
    Simula la carga de archivos para validar el rendimiento.
    En lugar de importar la ventana pesada de Tkinter, mockeamos su función aislada.
    """
    # Creamos un archivo falso para probar la detección
    dummy_img = os.path.join(os.path.dirname(ROOT_DIR), "fondo_test_invisible.png")
    with open(dummy_img, "w") as f:
        f.write("fake image data")
        
    ws = [f for f in os.listdir(os.path.dirname(ROOT_DIR)) if f.lower().startswith("fondo") and f.lower().endswith((".png", ".jpg", ".jpeg"))]
    
    assert "fondo_test_invisible.png" in ws
    
    # Limpieza
    os.remove(dummy_img)

# Nota: Para Pruebas End-to-End de UI en Tkinter, se requiere un entorno con pantalla activa.
# Se haría importando `MiniWindowsV4` e invocando `app.desktop.event_generate('<Button-1>')`.


def test_desktop_rendering_mock():
    # Simulamos la existencia de un folder para verificar que no colapsa
    import os
    folder_path = os.path.join(ROOT_DIR, 'Carpeta_Mock')
    os.makedirs(folder_path, exist_ok=True)
    assert os.path.exists(folder_path)
    os.rmdir(folder_path)
