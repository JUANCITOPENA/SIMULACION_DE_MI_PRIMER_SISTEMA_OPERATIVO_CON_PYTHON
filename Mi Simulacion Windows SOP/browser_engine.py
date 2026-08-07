# ==============================================================================
# MOTOR DE NAVEGACIÓN WEB AISLADO (browser_engine.py)
# ==============================================================================
# ¿Por qué existe este archivo separado del main.py?
# Mezclar librerías gráficas pesadas (Tkinter, Pygame y PyQt6) en un mismo
# hilo de ejecución provoca "Choques de Trenes" (Segmentation Faults). 
# Al aislar el navegador en este archivo, lo ejecutamos como un subproceso 
# independiente. 
#
# NUEVO (V2.1): ¡Inyección de Ventanas (Window Reparenting)!
# Mediante la API de Windows (ctypes), obligamos a este proceso aislado a 
# "vivir" físicamente dentro del Frame de Tkinter, creando una ilusión visual 
# de que el navegador es nativo del sistema simulado, manteniendo el aislamiento.
# ==============================================================================

import sys
import ctypes
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QMainWindow, QToolBar, QLineEdit, QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile

# Constantes de la API de Windows para manipulación de ventanas
GWL_STYLE = -16
WS_POPUP = 0x80000000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_CHILD = 0x40000000

class Browser(QMainWindow):
    def __init__(self, tk_hwnd=None, url="https://duckduckgo.com"):
        super().__init__()
        self.tk_hwnd = tk_hwnd
        # Configuramos el título y el tamaño base de nuestra ventana de navegación
        self.setWindowTitle("JPV Navegador Web (Modo Incógnito)")
        
        # --- SISTEMA ANTI-BLOQUEOS Y MODO INCÓGNITO ---
        self.profile = QWebEngineProfile("", None)
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        from PyQt6.QtWebEngineCore import QWebEnginePage
        self.page = QWebEnginePage(self.profile, self)
        
        # --- CONTENEDOR PRINCIPAL ---
        self.browser = QWebEngineView()
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        
        # --- BARRA DE NAVEGACIÓN (UI) ---
        navbar = QToolBar()
        self.addToolBar(navbar)
        
        back_btn = QAction("⬅️ Atrás", self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)
        
        forward_btn = QAction("➡️ Adelante", self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)
        
        reload_btn = QAction("🔄 Recargar", self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)
        
        home_btn = QAction("🏠 Inicio", self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        
        self.browser.urlChanged.connect(self.update_url)

        # Si estamos inyectados en Tkinter, creamos un auto-redimensionador
        if self.tk_hwnd:
            self.resize_timer = QTimer(self)
            self.resize_timer.timeout.connect(self.sync_size_with_parent)
            self.resize_timer.start(50) # Revisar tamaño cada 50ms (fluidez a 20 FPS)

    def sync_size_with_parent(self):
        """Usa la API de Windows para preguntar de qué tamaño es la ventana Padre de Tkinter y ajustarse a ella."""
        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
        rect = RECT()
        ctypes.windll.user32.GetClientRect(self.tk_hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width > 0 and height > 0:
            self.setGeometry(0, 0, width, height)

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://duckduckgo.com"))
        
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"): url = "https://" + url
        self.browser.setUrl(QUrl(url))
        
    def update_url(self, q):
        self.url_bar.setText(q.toString())

# --- PUNTO DE ENTRADA DEL SUBPROCESO ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Capturamos el HWND (Ventana ID) enviado por el Sistema Operativo (main_v2.py)
    tk_hwnd = int(sys.argv[1]) if len(sys.argv) > 1 else None
    
    window = Browser(tk_hwnd)
    
    if tk_hwnd:
        # MAGIA ARQUITECTÓNICA: Inyección del Subproceso
        qt_hwnd = int(window.winId())
        
        # 1. Le decimos a Windows: "Este proceso de PyQt6 ahora es hijo del proceso de Tkinter"
        ctypes.windll.user32.SetParent(qt_hwnd, tk_hwnd)
        
        # 2. Le quitamos los bordes, botones de cerrar y barra de título a PyQt6 para que parezca nativo
        # FIX CTYPES OVERFLOW: Usar funciones compatibles con 64-bits
        user32 = ctypes.windll.user32
        if sys.maxsize > 2**32:
            GetWindowLong = user32.GetWindowLongPtrW
            GetWindowLong.restype = ctypes.c_void_p
            SetWindowLong = user32.SetWindowLongPtrW
            SetWindowLong.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        else:
            GetWindowLong = user32.GetWindowLongW
            SetWindowLong = user32.SetWindowLongW
            
        style = GetWindowLong(qt_hwnd, GWL_STYLE)
        style = style & ~WS_POPUP & ~WS_CAPTION & ~WS_THICKFRAME
        style = style | WS_CHILD
        SetWindowLong(qt_hwnd, GWL_STYLE, style)
        
        window.showMaximized()
    else:
        window.show()
        
    sys.exit(app.exec())
