# ==============================================================================
# NÚCLEO DEL SISTEMA OPERATIVO: MINI WINDOWS V2.0 PRO
# Arquitectura: Monolítica con manejo de hilos (Multithreading) y eventos asíncronos.
# Autor: Ing. Juancito Peña | Propósito: Simulación Pedagógica de Alto Rendimiento.
# 
# Descripción Arquitectónica:
# ¡Bienvenidos, futuros Arquitectos de Software! Este archivo no es simplemente un script 
# común de Python. Se trata del núcleo (Kernel) y el Gestor de Ventanas (Window Manager) 
# de un simulador de Sistema Operativo altamente avanzado. Aquí se orquesta el manejo de 
# memoria, el renderizado de la interfaz gráfica a unos fluidos 60 cuadros por segundo (FPS) 
# utilizando CustomTkinter, y la gestión de acceso al disco duro virtual de forma segura 
# (sandboxing). Además, todo el entorno ha sido diseñado para persistir estados, es decir, 
# puede sobrevivir a cierres inesperados guardando la configuración en un archivo 'settings.json'.
# ¡Presten mucha atención a cómo cada módulo interactúa para lograr esta proeza!
# ==============================================================================

# ------------------------------------------------------------------------------
# SECCIÓN DE IMPORTACIONES (Módulos Base)
# ------------------------------------------------------------------------------
# En esta sección cargamos las bibliotecas necesarias para que nuestro SO funcione.
import customtkinter as ctk     # Motor gráfico principal para interfaces modernas (renderizado).
import datetime                 # Para el manejo del tiempo (reloj y timestamps).
import os                       # Interfaz vital con el SO real (acceso al file system).
import json                     # Serialización de datos (para guardar/leer configuraciones).
import psutil                   # Monitoreo de recursos reales (CPU, RAM, Discos).
import cv2                      # OpenCV para decodificar video cuadro por cuadro (Video Player).
import pygame                   # Motor de audio para reproducir sonidos sin bloqueos.
import threading                # Para ejecutar procesos pesados en segundo plano sin congelar la UI.
from tkinter import messagebox, simpledialog, filedialog # Diálogos nativos del sistema.
from tkinterweb import HtmlFrame # Motor de renderizado web interno.
from tkcalendar import Calendar  # Widget avanzado para el calendario del sistema.
from PIL import Image, ImageTk, ImageOps # Tratamiento avanzado de imágenes (Scaling/Cropping).
import moviepy as mp             # Herramienta para separar el audio de los videos (extracción multimedia).

# Inicializar Pygame Mixer: Preparamos el subsistema de audio para evitar latencias al reproducir sonidos.
pygame.mixer.init()

# ------------------------------------------------------------------------------
# CONFIGURACIÓN GLOBAL (Entorno Virtual y Sandboxing)
# ------------------------------------------------------------------------------
# Aquí establecemos las "fronteras" de nuestro sistema. Definimos dónde vive el disco 
# duro virtual, asegurándonos de que nuestras aplicaciones no toquen los archivos 
# reales del usuario (Sandboxing).
BASE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "SISTEMAS OPERATIVOS")
ROOT_DIR = os.path.join(BASE_PATH, "VIRTUAL_DRIVE")   # Unidad C: simulada.
TRASH_DIR = os.path.join(BASE_PATH, "RECYCLE_BIN")    # Papelera de reciclaje (borrado suave).
TEMP_DIR = os.path.join(BASE_PATH, "temp")            # Archivos temporales (ej: audio extraído).

# Si las carpetas base no existen, el Kernel se encarga de crearlas durante el booteo.
if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)
if not os.path.exists(TRASH_DIR): os.makedirs(TRASH_DIR)
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)

# Diccionario de Temas (Theming Engine):
# Estructura: [Color Principal, Color Hover, Color Fondo, Color Texto, Modo (dark/light)]
THEMES = {
    "Windows 11": ["#0078d4", "#2b88d8", "#202020", "white", "dark"],
    "Dark Cobalt": ["#1e3799", "#4a69bd", "#0c2461", "white", "dark"],
    "Emerald": ["#079992", "#38ada9", "#006266", "white", "dark"],
    "Sunset": ["#e55039", "#eb2f06", "#b71540", "white", "dark"],
    "Minimal White": ["#636e72", "#b2bec3", "#ffffff", "black", "light"]
}

# ==============================================================================
# CLASE: InternalWindow (Gestor de Ventanas MDI Avanzado)
# ==============================================================================
# En los sistemas operativos reales (como Windows o Linux), cada aplicación se dibuja 
# dentro de un 'Canvas' o contenedor aislado. Esta clase emula exactamente ese 
# comportamiento, lo que se conoce como MDI (Multiple Document Interface).
# 
# Técnicas arquitectónicas implementadas:
# - Física de Arrastre (Drag): Calcula los deltas matemáticos (X, Y) para mover la ventana 
#   fluídamente usando eventos del ratón en la barra de título.
# - Z-Index dinámico (Focus Management): Utiliza .lift() para traer la ventana al 
#   frente (encima de las demás) cuando el usuario hace clic sobre ella.
# - Aislamiento Gráfico (Layout Propagation): Impide que el contenido interno de 
#   la ventana altere o rompa el tamaño definido por el usuario usando 'pack_propagate(False)'.
# ==============================================================================
class InternalWindow(ctk.CTkFrame):
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, on_minimize=None, theme_colors=None, **kwargs):
        # Resolución de variables de tema (colores dinámicos basados en la configuración global)
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        title_bg = theme_colors[0] if theme_colors else "#34495e"
        text_col = theme_colors[3] if theme_colors else "white"
        
        # Invocamos al constructor de la superclase (CTkFrame) configurando bordes y colores
        super().__init__(master, width=width, height=height, corner_radius=10, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        # ¡CRÍTICO! Desactivar la propagación evita que los widgets hijos "estiren" la ventana,
        # rompiendo el tamaño físico que el Window Manager le asignó.
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Metadatos del proceso (Window State)
        self.app_id = app_id
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.is_maximized = False
        self.old_geometry = {"x": 300, "y": 100, "w": width, "h": height} # Memoria para el botón 'Restaurar'
        
        # --- Construcción de la Barra de Título (Title Bar) ---
        self.title_bar = ctk.CTkFrame(self, height=35, fg_color=title_bg, corner_radius=10)
        self.title_bar.pack(fill="x", side="top", padx=2, pady=2)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"), text_color=text_col)
        self.title_label.pack(side="left", padx=10)
        
        # Botones de control de ventana (Cerrar, Maximizar, Minimizar)
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, text_color=text_col, fg_color="#e81123", hover_color="#f1707a", command=self.close_window)
        self.close_btn.pack(side="right", padx=2)
        
        self.max_btn = ctk.CTkButton(self.title_bar, text="□", width=30, height=25, text_color=text_col, fg_color="transparent", hover_color="#555555", command=self.toggle_maximize)
        self.max_btn.pack(side="right", padx=2)
        
        self.min_btn = ctk.CTkButton(self.title_bar, text="_", width=30, height=25, text_color=text_col, fg_color="transparent", hover_color="#555555", command=self.minimize_window)
        self.min_btn.pack(side="right", padx=2)
        
        # Contenedor de contenido: Aquí es donde las "Apps" inyectarán sus interfaces
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        self.content.pack_propagate(False) # Aseguramos que el canvas de la app respete los límites
        
        # Grip de redimensionamiento (esquina inferior derecha)
        self.grip = ctk.CTkFrame(self, width=20, height=20, fg_color="transparent", cursor="sizing")
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        
        # Vinculación de eventos (Event Binding) para hacer que el sistema sea interactivo
        self.grip.bind("<B1-Motion>", self.do_resize) # Clic y arrastre para redimensionar
        self.title_bar.bind("<Button-1>", self.start_drag) # Inicio del arrastre de la ventana
        self.title_bar.bind("<B1-Motion>", self.do_drag)   # Movimiento de la ventana
        self.bind("<Button-1>", lambda e: self.lift())     # Cualquier clic en la ventana la trae al frente

        # Referencia al temporizador de redimensionamiento (debounce) para no saturar el CPU
        self._resize_job = None

    def start_drag(self, event):
        """Captura las coordenadas iniciales del ratón en el momento exacto del clic."""
        if self.is_maximized: return # No se puede arrastrar una ventana maximizada
        self._drag_data = {"x": event.x, "y": event.y}
        self.lift() # Traer ventana al frente

    def do_drag(self, event):
        """
        Calcula la nueva posición restando la posición original del clic y sumando
        la posición actual del ratón. Esto genera un arrastre "pegado" al puntero 1:1.
        """
        if self.is_maximized: return
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.place(x=x, y=y) # Movemos físicamente el marco de la ventana
        
    def do_resize(self, event):
        """
        Maneja el redimensionamiento dinámico. Utiliza un patrón 'debounce' (cancelando
        y reagendando con after()) para evitar renderizar demasiados cuadros por segundo
        durante el redimensionamiento brusco, manteniendo los 60FPS estables.
        """
        if self.is_maximized: return
        # Calculamos el nuevo ancho/alto asegurando límites mínimos (200x150)
        new_w = max(200, event.x_root - self.winfo_rootx())
        new_h = max(150, event.y_root - self.winfo_rooty())
        
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        # Diferimos el cambio 30ms para evitar parpadeos y sobrecarga del Event Loop
        self._resize_job = self.after(30, lambda: self._apply_resize(new_w, new_h))
        
    def _apply_resize(self, w, h):
        """Aplica las nuevas dimensiones a la ventana y actualiza el geometry manager."""
        self.configure(width=w, height=h)
        self.place(width=w, height=h)

    def toggle_maximize(self):
        """
        Maximiza la ventana o la restaura a su tamaño original.
        """
        if not self.is_maximized:
            self.old_geometry = {"x": self.winfo_x(), "y": self.winfo_y(), "w": self.winfo_width(), "h": self.winfo_height()}
            parent = self.master
            # En CustomTkinter no podemos pasar width/height a place(). Primero reconfiguramos y luego posicionamos.
            self.configure(width=parent.winfo_width(), height=parent.winfo_height())
            self.place(x=0, y=0)
            self.is_maximized = True
            self.grip.place_forget()
        else:
            self.configure(width=self.old_geometry["w"], height=self.old_geometry["h"])
            self.place(x=self.old_geometry["x"], y=self.old_geometry["y"])
            self.is_maximized = False
            self.grip.place(relx=1.0, rely=1.0, anchor="se")

    def minimize_window(self):
        """Oculta visualmente la ventana sin matarla. El proceso sigue en memoria."""
        if self.on_minimize: self.on_minimize(self.app_id)
        self.place_forget() # Elimina la ventana del Gestor de Geometría (pero sigue viva)

    def close_window(self):
        """Mata el proceso y destruye la ventana, liberando su memoria."""
        if self.on_close: self.on_close(self.app_id)
        self.destroy() # Libera el objeto de Tkinter

# ==============================================================================
# CLASE PRINCIPAL: MiniWindowsV4 (El Kernel y Bucle de Eventos Visual)
# ==============================================================================
# Esta es la raíz matemática, gráfica y orquestal de todo el emulador. Hereda 
# directamente de ctk.CTk, convirtiéndose en el 'Bucle de Eventos Principal' (Main Loop). 
# Actúa como un SystemD o init en sistemas UNIX, siendo el proceso padre (PID 1).
# 
# Desde aquí se coordina:
# 1. La carga de la "BIOS" y Configuraciones persistentes (load_settings).
# 2. El renderizado del Escritorio y la Barra de Tareas.
# 3. El despacho, monitoreo y terminación de procesos hijos (App Store, Terminal, etc.).
# ==============================================================================
class MiniWindowsV4(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración inicial del contenedor base
        self.title("Mini Windows JPV v4.2 - Multimedia Pro")
        self.geometry("1300x850") # Resolución nativa del simulador
        
        # Inicialización de subsistemas
        self.wallpapers = self.scan_wallpapers() # Indexar recursos gráficos
        self.load_settings() # Cargar el estado previo desde el disco (Persistencia)
        
        # Diccionario de procesos (Registro de la memoria activa)
        self.running_apps = {}
        
        # Validar consistencia del índice de fondo de pantalla (por si se borró una imagen)
        if self.current_wallpaper_idx >= len(self.wallpapers):
            self.current_wallpaper_idx = 0

        # --- Composición Visual: El Escritorio (Desktop) ---
        self.desktop = ctk.CTkFrame(self, corner_radius=0)
        self.desktop.pack(fill="both", expand=True)
        
        self.bg_label = ctk.CTkLabel(self.desktop, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1) # El fondo abarca el 100%
        # Evento <Configure>: Permite re-escalar el fondo cuando el usuario cambia el tamaño de la ventana madre
        self.bind("<Configure>", lambda e: self.load_wallpaper())
        
        # --- Composición Visual: La Barra de Tareas (Taskbar) ---
        self.taskbar = ctk.CTkFrame(self, height=55, fg_color=("#dfe6e9", "#2d3436"), corner_radius=0)
        self.taskbar.pack(side="bottom", fill="x")

        # Configuración del icónico "Menú Inicio"
        start_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "start.png")
        if os.path.exists(start_icon_path):
            start_img = ctk.CTkImage(light_image=Image.open(start_icon_path), size=(25, 25))
            self.start_btn = ctk.CTkButton(self.taskbar, text="", image=start_img, width=60, height=45,
                                            fg_color=THEMES[self.current_theme][0], hover_color="#555555",
                                            command=self.toggle_start_menu)
        else:
            self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=60, height=45,
                                            fg_color=THEMES[self.current_theme][0], 
                                            command=self.toggle_start_menu)
        self.start_btn.pack(side="left", padx=15, pady=5)
        
        # Contenedor para los procesos activos en la barra de tareas (Scroll horizontal)
        self.apps_tb_frame = ctk.CTkScrollableFrame(self.taskbar, fg_color="transparent", orientation="horizontal", height=45)
        self.apps_tb_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Subsistema de Audio: Controles de Volumen en el Tray System
        self.vol_frame = ctk.CTkFrame(self.taskbar, fg_color="transparent")
        self.vol_frame.pack(side="right", padx=20)
        self.vol_label = ctk.CTkLabel(self.vol_frame, text="🔊", font=("Segoe UI", 14))
        self.vol_label.pack(side="left", padx=5)
        
        # Slider de volumen que afecta globalmente a pygame.mixer
        self.vol_slider = ctk.CTkSlider(self.vol_frame, from_=0, to=1, width=100, command=self.change_volume)
        self.vol_slider.set(1.0); self.vol_slider.pack(side="left")

        # Reloj del Sistema
        self.clock_btn = ctk.CTkButton(self.taskbar, text="", font=("Consolas", 12, "bold"),
                                        fg_color="transparent", width=180, command=self.open_calendar)
        self.clock_btn.pack(side="right", padx=10)
        
        # --- Rutinas de Inicialización Final ---
        self.update_time() # Iniciar el bucle del reloj
        self.setup_desktop_icons() # Inyectar iconos en el escritorio
        
        # Punteros a los menús contextuales
        self.start_menu = None
        self.context_menu = None
        
        # Cargar el motor de renderizado de fondo (Wallpaper Engine)
        self.load_wallpaper()
        
        # Binding de eventos globales del ratón en el escritorio
        self.bg_label.bind("<Button-1>", self.on_desktop_click) # Clic izquierdo: cerrar menús abiertos
        self.bg_label.bind("<Button-3>", self.show_context_menu) # Clic derecho: abrir menú de opciones


    def load_settings(self):
        """
        Lee el archivo de configuración del disco (simulando lectura del registro o BIOS).
        Maneja fallos elegantemente: si no existe, inyecta valores por defecto seguros.
        """
        self.settings_file = os.path.join(ROOT_DIR, "settings.json")
        default_settings = {"theme": "Windows 11", "wallpaper_idx": 0, "volume": 1.0, "installed_apps": [], "icon_positions": {}}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    default_settings.update(data)
            except: pass # En caso de corrupción JSON, simplemente sobrevive con defaults
        
        # Aplicar el estado a las variables en memoria RAM del Kernel
        self.current_theme = default_settings["theme"]
        self.current_wallpaper_idx = default_settings["wallpaper_idx"]
        self.volume_level = default_settings["volume"]
        self.installed_apps = default_settings["installed_apps"]
        self.icon_positions = default_settings["icon_positions"]

    def save_settings(self):
        """
        Sobreescribe el archivo settings.json (Persistencia de datos).
        Cada vez que el usuario hace un cambio crítico (mover un icono, cambiar volumen, instalar app),
        llamamos a esta función para asegurar que el SO "recuerde" todo en su próximo booteo.
        """
        data = {
            "theme": self.current_theme,
            "wallpaper_idx": self.current_wallpaper_idx,
            "volume": getattr(self, "volume_level", 1.0),
            "installed_apps": getattr(self, "installed_apps", []),
            "icon_positions": getattr(self, "icon_positions", {})
        }
        try:
            with open(self.settings_file, "w") as f:
                json.dump(data, f)
        except Exception as e: 
            print(f"Error crítico al guardar la configuración: {e}")

    def get_wallpaper_dir(self):
        """Asegura que el directorio de activos gráficos (assets) exista."""
        wall_dir = os.path.join(BASE_PATH, "assets", "wallpapers")
        os.makedirs(wall_dir, exist_ok=True)
        return wall_dir

    def scan_wallpapers(self):
        """
        Escanea el disco duro en busca de imágenes soportadas.
        Incluye una lógica de 'Backward Compatibility' (compatibilidad hacia atrás)
        para migrar fondos de versiones antiguas a la nueva estructura de directorios.
        """
        wall_dir = self.get_wallpaper_dir()
        
        # Lógica de migración (Mueve fondos de versiones antiguas al nuevo directorio de activos)
        old_ws = [f for f in os.listdir(BASE_PATH) if f.lower().startswith("fondo") and f.lower().endswith((".png", ".jpg", ".jpeg"))]
        import shutil
        for old_w in old_ws:
            try: shutil.move(os.path.join(BASE_PATH, old_w), os.path.join(wall_dir, old_w))
            except: pass
            
        # Indexar recursos actuales
        ws = [f for f in os.listdir(wall_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        
        # Si el usuario borró todo, el SO debe auto-repararse creando un color base seguro.
        if not ws:
            img = Image.new('RGB', (1920, 1080), color = '#2c3e50')
            img.save(os.path.join(wall_dir, "default.png"))
            ws = ["default.png"]
        return sorted(ws)

    def load_wallpaper(self):
        """
        Motor de renderizado de fondo (Wallpaper Engine).
        Se encarga de cargar la imagen, redimensionarla proporcionalmente (usando el algoritmo de
        remuestreo de Lanczos para máxima nitidez) sin causar distorsión, independientemente
        de la resolución actual de la ventana madre.
        """
        try:
            fname = self.wallpapers[self.current_wallpaper_idx]
            path = os.path.join(self.get_wallpaper_dir(), fname)
            if not os.path.exists(path): return
            
            wall_img = Image.open(path)
            
            # --- AJUSTE MATEMÁTICO PROPORCIONAL (NO DISTORSIÓN) ---
            # Obtenemos las dimensiones físicas actuales del frame del escritorio
            win_w = self.desktop.winfo_width()
            win_h = self.desktop.winfo_height()
            
            # Condición de rescate: Si la ventana apenas se está creando (width=1), 
            # forzamos los valores del boot base (1300x850) para evitar división por cero.
            if win_w < 100 or win_h < 100: win_w, win_h = 1300, 850
            
            # ImageOps.fit realiza un 'crop & scale' perfecto, manteniendo la relación de aspecto.
            wall_img = ImageOps.fit(wall_img, (win_w, win_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            
            # Inyectamos el frame a CustomTkinter y lo renderizamos
            self.bg_image = ctk.CTkImage(wall_img, wall_img, size=(win_w, win_h))
            self.bg_label.configure(image=self.bg_image)
        except Exception as e: 
            print(f"Excepción en el renderizador de Wallpaper: {e}")

    def change_wallpaper(self):
        """Avanza al siguiente fondo usando aritmética modular (ciclado infinito)."""
        self.current_wallpaper_idx = (self.current_wallpaper_idx + 1) % len(self.wallpapers)
        self.load_wallpaper()

    def change_volume(self, value):
        """Intercepta los cambios en el slider y controla el volumen del mezclador de audio a bajo nivel."""
        self.volume_level = float(value)
        pygame.mixer.music.set_volume(self.volume_level) # Modificar el API del kernel de sonido
        
        # Feedback visual semántico basado en el nivel
        icon = "🔇" if self.volume_level == 0 else "🔉" if self.volume_level < 0.5 else "🔊"
        self.vol_label.configure(text=icon)
        
        self.save_settings() # Persistencia del volumen deseado

    def update_time(self):
        """
        Subrutina asíncrona que mantiene el reloj vivo.
        Llama al API de tiempo y se re-programa a sí misma usando 'after' de Tkinter
        exactamente cada 1000 milisegundos (1 segundo).
        """
        self.clock_btn.configure(text=datetime.datetime.now().strftime("%I:%M:%S %p\n%d/%m/%Y"))
        self.after(1000, self.update_time)

    def apply_theme(self, name):
        """
        Motor de temas en tiempo real (Theming Engine).
        Alterna entre esquemas de color globales (Modo oscuro, claro, acentos)
        sin necesidad de reiniciar el sistema operativo. ¡Magia pura en memoria RAM!
        """
        self.current_theme = name
        colors = THEMES[name]
        
        # Propagar cambios al núcleo gráfico de CustomTkinter
        ctk.set_appearance_mode(colors[4])
        self.start_btn.configure(fg_color=colors[0], hover_color=colors[1])
        
        # Recorremos el árbol de widgets buscando iconos del escritorio para aplicarles
        # el nuevo color de contraste de fuente (blanco en modo oscuro, negro en modo claro).
        txt_col = "white" if colors[4] == "dark" else "black"
        for child in self.desktop.winfo_children():
            if isinstance(child, ctk.CTkButton) and child != self.bg_label:
                child.configure(text_color=txt_col)
                
        messagebox.showinfo("Sistema Operativo", f"Tema '{name}' inyectado exitosamente en el DOM.")
        self.save_settings()

    # ==============================================================================
    # SISTEMA DE ARRASTRE Y FÍSICAS (DRAG & DROP DE ESCRITORIO)
    # ==============================================================================
    def make_draggable(self, widget, action_cmd, item_id):
        """
        Esta función dota de vida a los iconos del escritorio. En lugar de estar estáticos,
        permite al usuario hacer clic y moverlos por la pantalla (libertad total). Para evitar conflictos 
        entre 'hacer clic para abrir la app' y 'hacer clic para arrastrar', aplicamos matemáticas de deltas
        (distancia euclidiana aproximada).
        """
        def start_drag(event):
            # Guardamos las coordenadas exactas donde el usuario hizo clic por primera vez
            widget._drag_start_x = event.x
            widget._drag_start_y = event.y
            widget._is_dragged = False # Asumimos inicialmente que es un clic normal (intención de abrir)

        def do_drag(event):
            # Si el ratón se mueve más de 3 píxeles desde el origen, cambiamos el estado a 'Arrastrando'
            # (Anulamos la intención de abrir la app y procedemos a mover el widget).
            if abs(event.x - widget._drag_start_x) > 3 or abs(event.y - widget._drag_start_y) > 3:
                widget._is_dragged = True
                
            # Calculamos las nuevas coordenadas sumando el desplazamiento del ratón
            x = widget.winfo_x() - widget._drag_start_x + event.x
            y = widget.winfo_y() - widget._drag_start_y + event.y
            
            # --- FÍSICA DE LÍMITES Y COLISIONES (Screen Bounds) ---
            # Evitamos que el usuario arrastre el icono fuera de los bordes de la pantalla,
            # lo que causaría que el archivo se pierda eternamente en el abismo digital (fuera de la ventana).
            max_x = self.desktop.winfo_width() - widget.winfo_width()
            max_y = self.desktop.winfo_height() - widget.winfo_height()
            
            # Valores de rescate si el layout aún no se ha dibujado completamente.
            if max_x < 0: max_x = 1300 
            if max_y < 0: max_y = 850
            
            x = max(0, min(x, max_x)) # Restringimos el eje X entre 0 y el borde derecho
            y = max(0, min(y, max_y)) # Restringimos el eje Y entre 0 y el borde inferior
            
            widget.place(x=x, y=y) # Aplicamos la nueva posición física al renderizador
            
            # Guardamos temporalmente en memoria la nueva ubicación de este ítem
            self.icon_positions[item_id] = [x, y]

        def on_release(event):
            # Si el estado final fue un arrastre, consolidamos el cambio escribiéndolo en el disco duro (settings.json).
            # Si fue un clic limpio (sin desplazarse más de 3 píxeles), entonces ejecutamos el programa correspondiente.
            if getattr(widget, "_is_dragged", False):
                self.save_settings() # Guardar nuevas posiciones para la posteridad
            else:
                if action_cmd: action_cmd() # Llamada a la función (por ejemplo: open_explorer)

        # Interceptamos los eventos del ratón a nivel nativo de Tkinter, agregando (+) a eventos existentes
        widget.bind("<Button-1>", start_drag, add="+")
        widget.bind("<B1-Motion>", do_drag, add="+")
        widget.bind("<ButtonRelease-1>", on_release, add="+")

    def setup_desktop_icons(self):
        """
        Orquestador visual del Escritorio. Lee los componentes nativos (Mi PC, Papelera) y 
        luego escanea el Disco Duro Virtual en busca de archivos del usuario para dibujarlos.
        """
        # Memoria caché para referencias de imágenes (evita que el Garbage Collector borre los iconos)
        self.icon_images = getattr(self, "icon_images", {})
        
        # Metadatos Base: (Nombre Visible, Identificador RAM, Comando a ejecutar, Archivo PNG)
        icon_data = [
            ("Mi PC", "mypc", self.open_my_pc, "mypc.png"),
            ("Papelera", "trash", self.open_recycle_bin, "trash.jpg"),
            ("Explorador", "explorer", self.open_explorer, "explorer.png"),
            ("Navegador", "browser", self.open_browser, "browser.png"),
            ("Video Pro", "video", self.open_video_player, "video.png"),
            ("Notepad", "notepad", self.open_notepad, "notepad.png"),
            ("Configuración", "settings", self.open_control_panel, "settings.png"),
            ("Task Mgr", "taskmgr", self.open_task_manager, "start.png"),
            ("Terminal", "terminal", self.open_terminal, "start.png"),
            ("App Store", "store", self.open_app_store, "explorer.png")
        ]
        
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        
        # Posicionamiento inicial en cuadrícula (grid engine)
        y_pos = 30
        x_pos = 40
        
        # 1. Limpieza Total: Antes de repintar, borramos todos los iconos existentes para evitar duplicados.
        for widget in self.desktop.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()

        # 2. Inyección de Sistema: Renderizar iconos fijos (Sistema Operativo Core)
        for i, (name, aid, cmd, icon_file) in enumerate(icon_data):
            img_path = os.path.join(assets_dir, icon_file)
            img = None
            if os.path.exists(img_path):
                # Cargamos la textura
                img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                self.icon_images[aid] = img # Guardamos referencia en memoria fuerte
            
            # Crear el elemento en el lienzo
            btn = ctk.CTkButton(self.desktop, text=name, image=img, compound="top", width=100, height=90, text_color=("#000000", "#FFFFFF"), 
                                 fg_color="transparent", 
                                 hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 13, "bold"))
            # Inyectar las físicas de arrastre
            self.make_draggable(btn, cmd, aid)
            
            # ¿El usuario lo movió antes? Leer el mapa de posiciones
            if aid in self.icon_positions:
                pos = self.icon_positions[aid]
                btn.place(x=pos[0], y=pos[1])
            else:
                # Disposición en cuadrícula original
                btn.place(x=x_pos, y=y_pos)
                self.icon_positions[aid] = [x_pos, y_pos]
                
                # Algoritmo de desbordamiento (Word Wrap visual)
                y_pos += 110
                if y_pos > 600:
                    y_pos = 30
                    x_pos += 120

        # 3. Escaneo del Disco: Renderizar carpetas y archivos creados por el usuario
        if os.path.exists(ROOT_DIR):
            for item in os.listdir(ROOT_DIR):
                if item == "settings.json": continue # No mostrar el archivo BIOS
                item_path = os.path.join(ROOT_DIR, item)
                is_dir = os.path.isdir(item_path)
                
                # Reutilizamos los iconos del sistema para representar datos de usuario
                fallback_icon = "explorer.png" if is_dir else "notepad.png"
                img_path = os.path.join(assets_dir, fallback_icon)
                img = None
                if os.path.exists(img_path):
                    img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                    self.icon_images[item] = img
                    
                # Bindings dinámicos: Si es carpeta, explorador. Si es archivo, bloc de notas.
                if is_dir:
                    action = self.open_explorer
                else:
                    action = self.open_notepad
                    
                btn = ctk.CTkButton(self.desktop, text=item[:10], image=img, compound="top", width=100, height=90, text_color=("#000000", "#FFFFFF"), 
                                     fg_color="transparent", 
                                     hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 12))
                
                # Inyección de Menú Contextual (Clic derecho) individual por ítem
                btn.bind("<Button-3>", lambda e, p=item_path, d=is_dir: self.show_item_context_menu(e, p, d))
                
                self.make_draggable(btn, action, item)
                
                if item in self.icon_positions:
                    pos = self.icon_positions[item]
                    btn.place(x=pos[0], y=pos[1])
                else:
                    btn.place(x=x_pos, y=y_pos)
                    self.icon_positions[item] = [x_pos, y_pos]
                    y_pos += 110
                    if y_pos > 600:
                        y_pos = 30
                        x_pos += 120


    def toggle_start_menu(self):
        """
        Alterna la visibilidad del 'Menú de Inicio'. 
        Si está abierto, lo destruye (limpiando RAM). Si está cerrado, lo crea e inyecta
        un submenú con acceso rápido a programas y opciones de personalización.
        """
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        else:
            # Cerrar otros menús para mantener foco y limpieza en la UI
            if self.context_menu: self.context_menu.destroy(); self.context_menu = None
            
            # Instanciando el panel principal del Menú Inicio
            self.start_menu = ctk.CTkFrame(self.desktop, width=350, height=600, border_width=2, corner_radius=20)
            self.start_menu.pack_propagate(False)
            
            # Posicionamiento absoluto respecto a la ventana, amarrado a la esquina inferior izquierda
            self.start_menu.place(x=10, y=self.desktop.winfo_height() - 610)
            self.start_menu.lift() # Fuerza para renderizar sobre las apps abiertas
            
            ctk.CTkLabel(self.start_menu, text="SISTEMA JPV v4.2", font=("Segoe UI", 20, "bold")).pack(pady=20)
            
            scroll_f = ctk.CTkScrollableFrame(self.start_menu, fg_color="transparent")
            scroll_f.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Diccionario en tupla (Nombre UI, Puntero a función)
            apps = [("🗂️ Explorador", self.open_explorer), ("🌍 Navegador", self.open_browser), ("📽️ Video Player", self.open_video_player),
                    ("🖥️ Mi PC", self.open_my_pc), ("🗒️ Notepad", self.open_notepad), ("🧮 Calculadora", self.open_calc),
                    ("⚙️ Configuración", self.open_control_panel), ("📊 Task Manager", self.open_task_manager), ("💻 Terminal", self.open_terminal), ("🛒 App Store", self.open_app_store)]
            
            # Generación dinámica de la lista de aplicaciones
            for n, c in apps:
                # Al hacer clic: Ejecutamos el comando de la app y automáticamente ocultamos el menú inicio
                ctk.CTkButton(scroll_f, text=n, fg_color="transparent", text_color=("#000000", "#FFFFFF"), anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            
            ctk.CTkLabel(scroll_f, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=10)
            
            for tname in THEMES:
                ctk.CTkButton(scroll_f, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=20, pady=2)
            
            ctk.CTkButton(scroll_f, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=20, pady=15)

    def request_app(self, app_id, title, size):
        """
        El Administrador de Despachos (Dispatcher). Toda aplicación que desee abrirse,
        debe solicitar su 'Window Container' mediante esta función. 
        Si el proceso ya está activo, no abre duplicados, simplemente restaura y da foco
        a la ventana existente, ahorrando memoria valiosa.
        """
        if app_id in self.running_apps:
            self.restore_app(app_id) # La app ya vive, despiértala.
            return None
            
        # Nace un nuevo proceso. Se le asigna un 'InternalWindow' MDI.
        win = InternalWindow(self.desktop, app_id, title, *map(int, size.split('x')), 
                             on_close=self.on_app_close, on_minimize=self.on_app_minimize, theme_colors=THEMES[self.current_theme])
        
        # Registrar el proceso en el Task Manager interno
        self.running_apps[app_id] = win
        win.place(x=300, y=100) # Posición de spawn inicial predeterminada
        
        # Actualizamos la Taskbar para mostrar el nuevo proceso
        self.update_taskbar_buttons()
        return win # Retornamos el manejador (handler) para que la app inyecte sus widgets.

    def on_app_close(self, app_id):
        """Manejador de terminación. Un proceso ha muerto, debemos limpiar sus huellas en RAM."""
        if app_id in self.running_apps: 
            del self.running_apps[app_id] # Free/Deallocate memory reference
            self.update_taskbar_buttons()

    def on_desktop_click(self, event):
        """Manejador global (Click Tracker). Cuando el usuario clica el fondo vacío, colapsamos menús."""
        if getattr(self, "start_menu", None): self.start_menu.destroy(); self.start_menu = None
        if getattr(self, "context_menu", None): self.context_menu.destroy(); self.context_menu = None

    def show_context_menu(self, event):
        """Menú contextual estándar al dar clic derecho en el escritorio vacío."""
        self.on_desktop_click(None) # Oculta todo antes de abrir
        self.context_menu = ctk.CTkFrame(self.desktop, width=150, corner_radius=5, border_width=1, border_color="gray")
        self.context_menu.place(x=event.x, y=event.y) # Spawn exactamente en el puntero del mouse
        
        # Definición declarativa de opciones
        opts = [
            ("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.refresh_desktop()]),
            ("📁 Nueva Carpeta", lambda: [self.context_menu.destroy(), self.create_new_folder()]),
            ("📄 Nuevo Archivo", lambda: [self.context_menu.destroy(), self.create_new_file()]),
            ("🖼️ Cambiar Fondo", lambda: [self.context_menu.destroy(), self.open_wallpaper_selector()]),
            ("⚙️ Propiedades", lambda: [self.context_menu.destroy(), self.open_control_panel()])
        ]
        
        for name, cmd in opts:
            ctk.CTkButton(self.context_menu, text=name, anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"), 
                          hover_color="#555555", command=cmd).pack(fill="x", padx=2, pady=2)

    def show_item_context_menu(self, event, item_path, is_dir):
        """Menú contextual avanzado al dar clic derecho específicamente sobre un icono o carpeta del usuario."""
        self.on_desktop_click(None)
        self.context_menu = ctk.CTkFrame(self.desktop, width=150, corner_radius=5, border_width=1, border_color="gray")
        
        # Cálculo de offsets globales vs relativos para ubicar exactamente sobre el puntero
        self.context_menu.place(x=event.x_root - self.desktop.winfo_rootx(), y=event.y_root - self.desktop.winfo_rooty())
        
        opts = []
        # Lógica condicional: Las carpetas se "Abren", los archivos de texto se "Editan".
        if is_dir:
            opts.append(("📂 Abrir", lambda: [self.context_menu.destroy(), self.open_explorer(item_path)]))
        else:
            opts.append(("📄 Abrir/Editar", lambda: [self.context_menu.destroy(), self.open_notepad(item_path)]))
            
        opts.extend([
            ("✏️ Renombrar", lambda: [self.context_menu.destroy(), self.rename_item(item_path)]),
            ("🗑️ Borrar", lambda: [self.context_menu.destroy(), self.delete_item(item_path)]),
            ("⚙️ Propiedades", lambda: [self.context_menu.destroy(), self.show_properties(item_path)])
        ])
        
        for name, cmd in opts:
            ctk.CTkButton(self.context_menu, text=name, anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"), 
                          hover_color="#555555", command=cmd).pack(fill="x", padx=2, pady=2)

    # ==============================================================================
    # SISTEMA DE ARCHIVOS Y BORRADO SEGURO (VFS - VIRTUAL FILE SYSTEM)
    # ==============================================================================
    def delete_item(self, path):
        """
        Soft Delete (Borrado Suave): 
        En lugar de aplicar `os.remove()` y destruir los datos para siempre (Hard Delete), 
        usamos `shutil.move()` para desplazar los bytes a la carpeta segura TRASH_DIR. 
        Esto emula el comportamiento de una Papelera de Reciclaje real del entorno Windows.
        """
        if messagebox.askyesno("Confirmar Seguridad", f"¿Seguro que quieres mover {os.path.basename(path)} a la papelera?"):
            try:
                import shutil
                dest = os.path.join(TRASH_DIR, os.path.basename(path))
                
                # Manejo de conflictos: Si ya existe un archivo con ese nombre en la basura, lo sobreescribimos.
                if os.path.exists(dest):
                    if os.path.isdir(dest): shutil.rmtree(dest)
                    else: os.remove(dest)
                    
                shutil.move(path, TRASH_DIR) # Desterramos el archivo de su ubicación actual.
                self.setup_desktop_icons() # Repintamos el escritorio para reflejar la desaparición.
            except Exception as e: 
                messagebox.showerror("Kernel Panic (IO Error)", str(e))
            
    def open_recycle_bin(self):
        """Wrapper mágico: Abre el explorador pero apuntándolo hacia la ruta oculta de la Papelera."""
        self.open_explorer(TRASH_DIR)

    def rename_item(self, path):
        """Envuelve la llamada POSIX al sistema operativo para renombrar un inodo/fichero."""
        def on_submit(new_name):
            try:
                os.rename(path, os.path.join(os.path.dirname(path), new_name))
                self.setup_desktop_icons()
            except Exception as e: messagebox.showerror("Error FS", str(e))
        # Solicitamos el nombre al usuario usando un componente interno (no popups nativos feos)
        self.show_internal_input_dialog("Renombrar Objeto", "Nuevo nombre del archivo:", on_submit)

    def show_properties(self, path):
        """Llamada a `stat` del sistema operativo nativo para extraer metadatos (tamaño, fechas)."""
        try:
            st = os.stat(path)
            size = st.st_size
            # Parseando un timestamp de UNIX a un string humano
            created = datetime.datetime.fromtimestamp(st.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            msg = f"Nombre de Objeto: {os.path.basename(path)}\nTipo de Nodo: {'Directorio' if os.path.isdir(path) else 'Archivo'}\nPeso en Disco: {size} bytes\nFecha de Creación: {created}\nRuta Absoluta: {path}"
            messagebox.showinfo("Propiedades Estructurales", msg)
        except Exception as e: messagebox.showerror("Error de Metadatos", str(e))
                          
    def show_internal_input_dialog(self, title, prompt, on_submit):
        """
        Generador de Cuadros de Diálogo Custom (Internal UI API).
        Sustituye a `simpledialog.askstring()` logrando una integración nativa
        con CustomTkinter, preservando temas oscuros y bordes redondeados.
        """
        dialog = ctk.CTkFrame(self.desktop, width=320, height=160, corner_radius=15, border_width=2, border_color="gray", fg_color=("#ecf0f1", "#2c3e50"))
        dialog.place(relx=0.5, rely=0.5, anchor="center") # Centrado matemático
        dialog.pack_propagate(False)
        dialog.lift() # Asegurar prominencia visual sobre todas las demás ventanas

        ctk.CTkLabel(dialog, text=title, font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(dialog, text=prompt, font=("Segoe UI", 12)).pack()
        
        entry = ctk.CTkEntry(dialog, width=260)
        entry.pack(pady=10)
        entry.focus_set() # Autoselect del campo para escribir sin usar el mouse
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        def submit(event=None):
            val = entry.get()
            dialog.destroy()
            if val: on_submit(val) # Dispara el callback (patrón de diseño Observer/Callback)
                
        def cancel():
            dialog.destroy()
            
        ctk.CTkButton(btn_frame, text="Aceptar", width=100, command=submit).pack(side="left", padx=25)
        ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="#e81123", hover_color="#f1707a", command=cancel).pack(side="right", padx=25)
        
        entry.bind("<Return>", submit) # Permite al usuario presionar 'ENTER' para aceptar.

    def refresh_desktop(self):
        """
        Rutina visual. Oculta temporalmente los iconos y los vuelve a dibujar
        después de un delay (250ms), lo que causa un ligero parpadeo.
        Esto estimula la psicología del usuario imitando cómo refresca (F5) un Windows real.
        """
        for widget in self.desktop.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget != self.bg_label:
                widget.place_forget()
        self.update() # Fuerza a Tkinter a dibujar la pantalla vacía
        self.after(250, lambda: [self.load_wallpaper(), self.setup_desktop_icons()]) # Reconstrucción asíncrona

    def create_new_folder(self):
        def on_submit(name):
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            self.setup_desktop_icons()
        self.show_internal_input_dialog("Sistema de Archivos", "Nombre de la nueva carpeta:", on_submit)
            
    def create_new_file(self):
        def on_submit(name):
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("") # Crea archivo vacío ('touch' de linux)
            self.setup_desktop_icons()
        self.show_internal_input_dialog("Sistema de Archivos", "Nombre completo del archivo (ej. notas.txt):", on_submit)

    def update_taskbar_buttons(self):
        """
        Orquesta la barra de tareas inferior. Escanea la tabla de procesos activos
        (`running_apps`) y crea un botón por cada uno, permitiendo restaurarlos al clic.
        """
        # Limpieza (Garbage Collect visual)
        for widget in self.apps_tb_frame.winfo_children():
            widget.destroy()
            
        # Repoblación
        for app_id, win in self.running_apps.items():
            btn = ctk.CTkButton(self.apps_tb_frame, text=win.title_label.cget("text"), width=120, height=30,
                                fg_color="transparent", text_color=("#000000", "#FFFFFF"), border_width=1, border_color="gray",
                                hover_color="#555555", command=lambda aid=app_id: self.restore_app(aid))
            btn.pack(side="left", padx=5)

    def restore_app(self, app_id):
        """Trae una aplicación minimizada de vuelta a la vida visual restaurando sus coordenadas."""
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            # Solo actuamos si la ventana está actualmente invisible
            if not win.winfo_viewable():
                win.place(x=win.old_geometry.get("x", 300), y=win.old_geometry.get("y", 100), 
                          width=win.old_geometry.get("w", win.winfo_width()), height=win.old_geometry.get("h", win.winfo_height()))
            win.lift()

    def on_app_minimize(self, app_id):
        """Hook invocado justo antes de minimizar. Salva el estado espacial para poder restaurarla."""
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            win.old_geometry = {"x": win.winfo_x(), "y": win.winfo_y(), "w": win.winfo_width(), "h": win.winfo_height()}

    # ==============================================================================
    # 🎬 VIDEO PLAYER PRO (STREAMING + MOTOR DE AUDIO ASÍNCRONO MULTITHREADING)
    # ==============================================================================
    # Leer video cuadro a cuadro en Python puede congelar la interfaz (GUI freeze).
    # Esta aplicación emplea una arquitectura compleja:
    # 1. Utiliza MoviePy en un hilo (Thread) separado para extraer el audio al vuelo.
    # 2. Utiliza PyGame Mixer para inyectar ese audio a la tarjeta de sonido de la PC real.
    # 3. Utiliza OpenCV (cv2) para leer matriz por matriz de pixeles (Frames) y renderizarlos
    #    usando ciclos `.after()` cortos, asegurando sincronización Audio-Video.
    # ==============================================================================
    def open_video_player(self):
        win = self.request_app("video", "JPV Video Pro (Advanced Engine)", "800x650")
        if not win: return
        
        # Invocamos el puente nativo con el SO del usuario para elegir el MP4
        vpath = filedialog.askopenfilename(filetypes=[("Video Multimedia", "*.mp4 *.avi")])
        if not vpath: win.destroy(); return
        
        # Hilo de Fondo (Daemon Thread) para separación de audio usando pipeline FFMPEG interno
        audio_temp = os.path.join(TEMP_DIR, "temp_audio.mp3")
        def extract():
            try:
                clip = mp.VideoFileClip(vpath)
                clip.audio.write_audiofile(audio_temp, logger=None) # logger=None calla los prints en terminal
                pygame.mixer.music.load(audio_temp)
                pygame.mixer.music.play()
            except Exception as e: print("Error en subsistema de audio:", e)
            
        # Iniciamos el proceso multihilo que no detendrá el renderizado de la UI
        threading.Thread(target=extract, daemon=True).start()

        # Configuración del objeto captura visual (Stream)
        cap = cv2.VideoCapture(vpath)
        total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        canvas = ctk.CTkLabel(win.content, text="")
        canvas.pack(fill="both", expand=True)
        
        # ENGANCHE DE CIERRE (KILL SWITCH) AUDIO/VIDEO:
        # Tkinter cancela los callbacks after() al destruir la ventana,
        # así que debemos forzar la parada del motor de audio aquí.
        original_close = win.on_close
        def custom_video_close(aid):
            pygame.mixer.music.stop() # Silenciar la RAM de Pygame
            try: cap.release() # Liberar punteros C++ de OpenCV
            except: pass
            if original_close: original_close(aid)
        win.on_close = custom_video_close
        
        # Barra de progreso y búsqueda (Time seeking)
        # Sincroniza al moverla el frame de OpenCV y el salto en segundos de PyGame Music
        seek = ctk.CTkSlider(win.content, from_=0, to=total_f, height=15, 
                             command=lambda v: [cap.set(cv2.CAP_PROP_POS_FRAMES, int(v)), 
                                                pygame.mixer.music.play(start=int(v)/cap.get(cv2.CAP_PROP_FPS))])
        seek.pack(fill="x", pady=5)
        
        self.is_playing = True
        def toggle():
            self.is_playing = not self.is_playing
            if self.is_playing: pygame.mixer.music.unpause()
            else: pygame.mixer.music.pause()

        ctk.CTkButton(win.content, text="Play/Pausa", command=toggle).pack(pady=5)

        # Bucle central de renderizado asíncrono
        def stream():
            # Validar existencia antes de renderizar
            if not win.winfo_exists(): return
                
            if self.is_playing:
                ret, frame = cap.read() # Obtener frame en formato BGR (Nativo de OpenCV)
                if ret:
                    seek.set(int(cap.get(cv2.CAP_PROP_POS_FRAMES)))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Transmutar matriz de colores para PIL
                    
                    # Conservación matemática del 'Aspect Ratio' original, centrando imagen
                    img = Image.fromarray(frame)
                    img = ImageOps.contain(img, (750, 450))
                    imgtk = ImageTk.PhotoImage(image=img)
                    
                    canvas.imgtk = imgtk # Evitar barrido por Garbage Collector
                    canvas.configure(image=imgtk)
            
            # Recurrir en 25ms logra una ilusión de ~40 FPS muy suaves
            win.after(25, stream)
            
        stream() # Iniciar latido

    # ==============================================================================
    # APLICACIONES CORE DEL SISTEMA
    # ==============================================================================

    def open_explorer(self, path=ROOT_DIR):
        """
        Navegador de Archivos Base (Explorer Engine).
        Construye una UI dinámica leyendo recursivamente los directorios del VFS (Virtual File System).
        """
        win = self.request_app("explorer", f"Explorador - {os.path.basename(path) or 'Raíz'}", "700x500")
        if not win: return
        
        nav = ctk.CTkFrame(win.content, height=40); nav.pack(fill="x", pady=2)
        
        # Botón para navegar al nivel superior (Cerrando la vista actual y despachando la nueva recursivamente)
        ctk.CTkButton(nav, text="⬆️ Subir Nivel", width=70, 
                      command=lambda: [win.destroy(), self.on_app_close("explorer"), self.open_explorer(os.path.dirname(path))]).pack(side="left", padx=5)
                      
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True)
        
        # Lectura del disco y mapeo visual
        for item in os.listdir(path):
            fp = os.path.join(path, item); is_d = os.path.isdir(fp)
            # Componente accionado. Si es ruta: bucle recursivo explorador. Si es archivo: Editor.
            ctk.CTkButton(scroll, text=f"{'📁' if is_d else '📄'} {item}", anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"), 
                          command=lambda p=fp: [win.destroy(), self.on_app_close("explorer"), self.open_explorer(p)] if os.path.isdir(p) else self.open_notepad(p)).pack(fill="x")

    def open_browser(self):
        """
        Lanza el navegador PyQt6 y lo incrusta mágicamente en Tkinter.
        Primero creamos nuestra ventana simulada. Luego, obtenemos su 'ID Nativo' 
        (HWND) y se lo pasamos al subproceso de PyQt6 para que use SetParent()
        y se renderice directamente dentro del simulador.
        """
        win = self.request_app("browser", "Navegador Web", "1024x768")
        if not win: return
        
        # Forzamos una actualización visual para que Tkinter asigne un HWND real
        self.update_idletasks()
        
        # Obtenemos el identificador de ventana de Windows
        tk_hwnd = str(win.content.winfo_id())
        
        import subprocess, sys
        browser_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_engine.py")
        
        # Inyectamos el ID como argumento al script
        p = subprocess.Popen([sys.executable, browser_script, tk_hwnd])
        
        # ENGANCHE DE CIERRE (KILL SWITCH): Evita que el proceso quede "Zombi"
        # Si el usuario cierra el InternalWindow, interceptamos el evento y matamos al hijo.
        original_close = win.on_close
        def custom_close(aid):
            try: p.kill() # Asesinato del subproceso Chromium
            except: pass
            if original_close: original_close(aid)
        win.on_close = custom_close

    def open_my_pc(self):
        """Dashboard estadístico del Sistema de Archivos y Discos Duros."""
        win = self.request_app("mypc", "Centro de Equipo (Mi PC)", "650x550")
        if not win: return
        
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Sección 1: Carpetas Frecuentes ---
        ctk.CTkLabel(scroll, text="Carpetas Principales del Sistema", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(0, 10))
        folders_f = ctk.CTkFrame(scroll, fg_color="transparent")
        folders_f.pack(fill="x")
        
        folders = [("Desktop", "Escritorio"), ("Downloads", "Descargas"), ("Documents", "Documentos"), ("Pictures", "Imágenes")]
        for i, (f_icon, f_name) in enumerate(folders):
            folder_path = ROOT_DIR if f_icon == "Desktop" else os.path.join(ROOT_DIR, f_name)
            os.makedirs(folder_path, exist_ok=True) # Crear si es primer uso
            
            btn = ctk.CTkButton(folders_f, text=f"📁 {f_name}", width=120, height=40, fg_color=("#dfe6e9", "#2d3436"), hover_color="#555555", text_color=("#000000", "#FFFFFF"),
                                command=lambda path=folder_path: [win.destroy(), self.on_app_close("mypc"), self.open_explorer(path)])
            btn.grid(row=0, column=i, padx=10, pady=5)
            
        self.setup_desktop_icons() # Asegurar sincronización en memoria
            
        # --- Sección 2: Discos Duros (Hardware Real vía Psutil) ---
        ctk.CTkLabel(scroll, text="Dispositivos, Puertos y Unidades", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(20, 10))
        
        for p in psutil.disk_partitions():
            try:
                # Lectura real del hardware físico de la computadora anfitrión
                u = psutil.disk_usage(p.mountpoint)
                f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
                f.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(f, text="💾", font=("Segoe UI", 28)).pack(side="left", padx=20, pady=10)
                
                info = ctk.CTkFrame(f, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, pady=10)
                
                ctk.CTkLabel(info, text=f"Volumen Físico Local ({p.device[:2]})", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
                
                # Renderizar barra de capacidad matemática
                pg = ctk.CTkProgressBar(info, height=12, progress_color="#0984e3")
                pg.pack(fill="x", pady=5, padx=5)
                pg.set(u.percent/100) # Normalización de rango (0.0 a 1.0)
                
                # Operaciones bitwise (Shift) para pasar rápidamente de Bytes a GigaBytes (`// 2**30`)
                ctk.CTkLabel(info, text=f"{u.free//2**30} GB disponibles de {u.total//2**30} GB totales", font=("Segoe UI", 11), text_color=("#444444", "#AAAAAA"), anchor="w").pack(fill="x")
            except: continue

    def open_notepad(self, path=None):
        """Bloc de Notas: Permite editar cualquier nodo que se pueda interpretar en ASCII/UTF-8."""
        win = self.request_app("notepad", "Editor de Texto Nativo", "600x500")
        if not win: return
        
        txt = ctk.CTkTextbox(win.content, font=("Consolas", 14)); txt.pack(fill="both", expand=True)
        
        # Precargar buffer si nos mandan una ruta de archivo.
        if path:
            with open(path, "r") as f: txt.insert("0.0", f.read())
            
        def save():
            # Si el archivo era nuevo (sin ruta), invocamos el diálogo del SO anfitrión, pero encapsulado en ROOT_DIR.
            p = path or filedialog.asksaveasfilename(initialdir=ROOT_DIR, defaultextension=".txt")
            if p:
                with open(p, "w") as f: f.write(txt.get("0.0", "end"))
                messagebox.showinfo("IO Manager", "Datos escritos al sector con éxito."); win.destroy(); self.on_app_close("notepad")
                
        ctk.CTkButton(win.content, text="💾 Guardar Cambios al Disco", command=save, fg_color="#00b894").pack(pady=10)

    def open_calc(self):
        """Calculadora Numérica construida enteramente en Grid Management."""
        win = self.request_app("calc", "Matemática Aplicada", "320x450")
        if not win: return
        
        ent = ctk.CTkEntry(win.content, font=("Consolas", 24), justify="right"); ent.pack(fill="x", padx=10, pady=15)
        grid = ctk.CTkFrame(win.content); grid.pack(fill="both", expand=True)
        
        btns = ['7','8','9','/','4','5','6','*','1','2','3','-','C','0','=','+']
        r, c = 0, 0
        
        # Autogeneración de Matriz (Layout Algorithm)
        for b in btns:
            # Lambda avanzado: Inyecta el caracter, pero si es 'C' borra el buffer, y si es '=' invoca `eval` de Python como motor algebraico.
            ctk.CTkButton(grid, text=b, width=65, height=65, text_color=("#000000", "#FFFFFF"), command=lambda x=b: [ent.insert("end", x) if x not in ["=","C"] else (ent.delete(0,"end") if x=="C" else ent.insert("end","="+str(eval(ent.get()))))]).grid(row=r, column=c, padx=3, pady=3)
            c+=1; 
            if c>3: c=0; r+=1 # Cambio de fila y reseteo de columna

    def open_calendar(self):
        win = self.request_app("calendar", "Sincronización Temporal", "400x500")
        if not win: return
        Calendar(win.content).pack(pady=10, padx=10, fill="both", expand=True)

    def open_wallpaper_selector(self):
        """Motor de despliegue de UI visual (Grid Scroll) para selección de fondos miniatura."""
        win = self.request_app("wallpapers", "Centro de Temas Visuales", "600x450")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        wall_dir = self.get_wallpaper_dir()
        ctk.CTkLabel(scroll, text=f"Directorio de texturas:\\n{wall_dir}", font=("Segoe UI", 12), text_color=("#444444", "#AAAAAA")).pack(pady=(0,10))
        
        grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        
        row, col = 0, 0
        for idx, w in enumerate(self.wallpapers):
            path = os.path.join(wall_dir, w)
            if os.path.exists(path):
                try:
                    # Generador de Miniaturas (Thumbnails) para no gastar demasiada RAM cargando las texturas 1080p
                    thumb_img = Image.open(path)
                    thumb_img = ImageOps.fit(thumb_img, (140, 90), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                    thumb = ctk.CTkImage(light_image=thumb_img, size=(140, 90))
                    
                    btn = ctk.CTkButton(grid_frame, image=thumb, text="", width=150, height=100, fg_color="transparent", hover_color="#555555",
                                        command=lambda i=idx: [setattr(self, 'current_wallpaper_idx', i), self.load_wallpaper(), self.save_settings()])
                    btn.grid(row=row, column=col, padx=10, pady=10)
                    
                    col += 1
                    if col > 2:
                        col = 0
                        row += 1
                except: continue

    def open_control_panel(self):
        """Dashboard de Análisis e Inyección de Temas."""
        win = self.request_app("settings", "Panel de Control Master", "600x450")
        if not win: return
        ctk.CTkLabel(win.content, text="⚙️ Configuración Maestra del Sistema", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        f_tema = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
        f_tema.pack(fill="x", pady=10)
        ctk.CTkLabel(f_tema, text="🎨 Arquitectura de Apariencia", font=("Segoe UI", 16, "bold")).pack(pady=5)
        
        themes_frame = ctk.CTkFrame(f_tema, fg_color="transparent")
        themes_frame.pack(pady=10)
        for tname in THEMES:
            ctk.CTkButton(themes_frame, text=tname, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(side="left", padx=5)
            
        f_sys = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
        f_sys.pack(fill="x", pady=10)
        
        ctk.CTkLabel(f_sys, text="💻 Telemetría de Hardware (Monitor de Host)", font=("Segoe UI", 16, "bold")).pack(pady=5)
        ram = psutil.virtual_memory()
        ctk.CTkLabel(f_sys, text=f"Memoria RAM Total Instalada: {ram.total // (1024**3)} GB", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(f_sys, text=f"Estrés Actual RAM: {ram.percent}%", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(f_sys, text=f"Carga en Procesador (CPU): {psutil.cpu_percent()}%", font=("Segoe UI", 14)).pack(pady=(0, 10))

    def open_task_manager(self):
        """
        Observador de Procesos (Task Manager).
        Se amarra asíncronamente al diccionario `self.running_apps` para renderizar el 
        estado de la memoria cada 2 segundos. Permite invocar la terminación forzosa de la clase
        InternalWindow (Matar un proceso, equivalente a kill -9).
        """
        win = self.request_app("taskmgr", "Administrador de Tareas (PID Watcher)", "400x500")
        if not win: return
        ctk.CTkLabel(win.content, text="📋 Tabla de Procesos Activos (Kernel RAM)", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        self.task_list_frame = ctk.CTkScrollableFrame(win.content)
        self.task_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.task_widgets = {} # Guarda ref a frames GUI existentes (Component State)
        
        def refresh_tasks():
            if not win.winfo_exists(): return
            
            current_apps = list(self.running_apps.keys())
            
            # --- Recolector de Basura Visual ---
            # Borrar barras (frames) de procesos que ya murieron (limpiamos el DOM).
            for tid in list(self.task_widgets.keys()):
                if tid not in current_apps:
                    self.task_widgets[tid].destroy()
                    del self.task_widgets[tid]
            
            # --- Inyector Visual ---
            # Añadir barras de procesos nuevos que no estén en la UI.
            for app_id, app_win in list(self.running_apps.items()):
                if app_id not in self.task_widgets:
                    f = ctk.CTkFrame(self.task_list_frame, fg_color=("#dfe6e9", "#2d3436"), corner_radius=5)
                    f.pack(fill="x", pady=2)
                    ctk.CTkLabel(f, text=app_win.title_label.cget("text")).pack(side="left", padx=10, pady=5)
                    
                    # El Botón Muerte: Despacha la orden de destrucción
                    ctk.CTkButton(f, text="Finalizar Árbol", fg_color="#e17055", hover_color="#d63031", width=60, height=24,
                                  command=lambda aid=app_id: self.running_apps[aid].close_window() if aid in self.running_apps else None).pack(side="right", padx=10)
                    self.task_widgets[app_id] = f
            
            win.after(2000, refresh_tasks) # Latido asíncrono para mantener UI fresca
            
        refresh_tasks()

    def open_app_store(self):
        """Simulador Lúdico de Tienda (Para fines pedagógicos, simula descargas falsas progresivas)."""
        win = self.request_app("store", "Repositorio de Paquetes (App Store)", "600x450")
        if not win: return
        
        ctk.CTkLabel(win.content, text="🛒 Centro Autorizado de Software", font=("Segoe UI", 24, "bold")).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        apps_disp = [
            ("Snake Game Engine", "Motor renderizador 2D clásico de Atari.", "snake"),
            ("WordPad Professional", "Procesador de textos estructurado en DOM.", "wordpad"),
            ("Calculadora Científica", "Algoritmos trigonométricos puros.", "calc_pro")
        ]
        
        def download_app(app_id, btn, bar):
            """Animador UI (Simulador de I/O por red)."""
            btn.configure(state="disabled", text="Descargando Paquetes...")
            
            def finish():
                btn.configure(text="¡Firmado e Instalado!", fg_color="green")
                if app_id not in self.installed_apps:
                    self.installed_apps.append(app_id) # Guardado en registro del Kernel
                    self.save_settings()
                messagebox.showinfo("Log de Red", f"Firma GPG comprobada. Aplicación {app_id} instalada en tu sistema.")
            
            # Bucle recursivo con delay (Simulación de ping y descarga chunk x chunk)
            def step(progress=0.0):
                if progress >= 1.0: finish(); return
                bar.set(progress)
                win.after(100, lambda: step(progress + 0.05))
                
            step()

        # Construcción visual de la galería
        for name, desc, appid in apps_disp:
            f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
            f.pack(fill="x", pady=10)
            
            info_f = ctk.CTkFrame(f, fg_color="transparent")
            info_f.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            ctk.CTkLabel(info_f, text=name, font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info_f, text=desc, font=("Segoe UI", 12), anchor="w").pack(fill="x")
            
            bar = ctk.CTkProgressBar(f, width=100)
            bar.pack(side="left", padx=10)
            bar.set(0) # Inicializar progreso vacío
            
            # Lógica de botón inteligente: Si la app ya estaba instalada en un booteo anterior, no permite descargar
            is_installed = appid in getattr(self, 'installed_apps', [])
            btn = ctk.CTkButton(f, text="Instalado" if is_installed else "Descargar", text_color=("#000000", "#FFFFFF"), 
                                width=90, fg_color="green" if is_installed else "#0984e3",
                                state="disabled" if is_installed else "normal")
            # Paso por referencia para no confundir variables locales de Python en bucles Lambda
            btn.configure(command=lambda aid=appid, b=btn, br=bar: download_app(aid, b, br))
            btn.pack(side="right", padx=15, pady=15)


    # ==============================================================================
    # 💻 MOTOR DE TERMINAL Y CONSOLA A NIVEL KERNEL (COMMAND LINE INTERFACE - CLI)
    # ==============================================================================
    # La terminal es un intérprete de comandos simulado (Shell). En lugar de enviar 
    # comandos peligrosos (como rm -rf) al sistema operativo anfitrión, los 'parseamos'
    # (analizamos) y los ejecutamos dentro de un entorno encapsulado (Sandboxing de Python).
    # Este shell solo tiene jurisdicción dentro de la carpeta VIRTUAL_DRIVE.
    # Empleamos buffers de texto inmutables para guardar el historial, exactamente
    # como funciona la consola CMD.exe nativa de Windows.
    # ==============================================================================
    def open_terminal(self):
        win = self.request_app("terminal", "JPV Shell (Emulador CLI de Bash/CMD)", "600x400")
        if not win: return
        win.content.configure(fg_color="black") # Hacker Mode
        
        # Buffer de salida estándar (STDOUT). Es 'disabled' para que el usuario no escriba aquí, solo lea.
        output_txt = ctk.CTkTextbox(win.content, fg_color="black", text_color="#00ff00", font=("Consolas", 14), state="disabled")
        output_txt.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Línea de comandos interactiva
        input_frame = ctk.CTkFrame(win.content, fg_color="black")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        prompt_label = ctk.CTkLabel(input_frame, text="C:\\VIRTUAL_DRIVE> ", text_color="#00ff00", font=("Consolas", 14))
        prompt_label.pack(side="left")
        
        cmd_var = ctk.StringVar()
        cmd_entry = ctk.CTkEntry(input_frame, textvariable=cmd_var, fg_color="black", text_color="#00ff00", border_width=0, font=("Consolas", 14))
        cmd_entry.pack(side="left", fill="x", expand=True)
        cmd_entry.focus() # Focalizar para escritura inmediata
        
        self.current_term_dir = ROOT_DIR # Cursor lógico del directorio actual (PWD - Print Working Directory)

        def get_prompt():
            """Calcula la ruta relativa para engañar al usuario, haciéndole creer que su VIRTUAL_DRIVE es la raíz 'C:\'"""
            rel = os.path.relpath(self.current_term_dir, ROOT_DIR)
            if rel == "." or rel.startswith(".."):
                self.current_term_dir = ROOT_DIR # Mecanismo de defensa (Jail): Prevenir escape (Directory Traversal)
                return "C:\\VIRTUAL_DRIVE> "
            return f"C:\\VIRTUAL_DRIVE\\{rel}> "

        def update_prompt():
            prompt_label.configure(text=get_prompt())
        
        def log(text):
            """Función proxy para inyectar cadenas de texto simulando el flujo STDOUT."""
            output_txt.configure(state="normal") # Abrir permiso escritura
            output_txt.insert("end", text + "\n")
            output_txt.configure(state="disabled") # Cerrar permiso
            output_txt.see("end") # Auto-scroll agresivo hacia abajo

        # Secuencia Boot-Up (MOTD - Message Of The Day)
        log("Mini Windows JPV Shell - Arquitectura x64 [Versión 2.0]")
        log("(c) Coded by Ing. Juancito Peña. Entorno pedagógico ultra-seguro.\n")
        
        def execute_command(event=None):
            """
            El 'Lexer' y 'Parser' del compilador interno.
            Troza el texto en fragmentos (splits) y evalúa el comando raíz (index 0).
            """
            command = cmd_var.get().strip()
            if not command: return # Ignorar 'Enters' vacíos
            
            cmd_var.set("") # Limpiar el input box
            log(f"{get_prompt()}{command}") # Hacer eco de la acción
            
            parts = command.split() # Tokenización
            cmd = parts[0].lower() # Comando base (case insensitive)
            
            # --- EVALUACIÓN HEURÍSTICA DE COMANDOS (IF-ELSE LADDER) ---
            if cmd == "help":
                log("Comandos Registrados: help, dir, cd <dir>, mkdir <dir>, type <file>, clear, echo, date, exit")
            elif cmd == "dir" or cmd == "ls":
                try:
                    log(f" Listando Directorio Inodo de {get_prompt()[:-2]}")
                    log("")
                    for item in os.listdir(self.current_term_dir):
                        full_path = os.path.join(self.current_term_dir, item)
                        is_dir = "<DIR>" if os.path.isdir(full_path) else "     "
                        log(f"{is_dir}\t{item}")
                except Exception as e:
                    log(f"OS Access Error: {e}")
            elif cmd == "cd":
                # Cambiar directorio (State Transition)
                if len(parts) > 1:
                    target = " ".join(parts[1:])
                    if target == "..":
                        self.current_term_dir = os.path.dirname(self.current_term_dir)
                    else:
                        new_dir = os.path.join(self.current_term_dir, target)
                        if os.path.isdir(new_dir):
                            self.current_term_dir = new_dir
                        else:
                            log("Fatal: El núcleo no puede resolver la ruta de memoria especificada.")
                    update_prompt()
            elif cmd == "mkdir" or cmd == "md":
                if len(parts) > 1:
                    target = " ".join(parts[1:])
                    try:
                        os.makedirs(os.path.join(self.current_term_dir, target), exist_ok=True)
                        self.setup_desktop_icons() # Avisarle al Gestor de Ventanas para actualizar escritorio
                    except Exception as e:
                        log(f"Permiso Denegado (Error POSIX): {e}")
                else: log("Sys-Warning: Faltan operandos. Sintaxis: mkdir [nombre_carpeta]")
            elif cmd == "type" or cmd == "cat":
                if len(parts) > 1:
                    target = " ".join(parts[1:])
                    target_file = os.path.join(self.current_term_dir, target)
                    if os.path.isfile(target_file):
                        try:
                            with open(target_file, "r") as f: log(f.read())
                        except Exception as e: log(f"Stream Error en I/O: {e}")
                    else: log("Fatal: Puntero colgado. Archivo no hallado.")
                else: log("Sys-Warning: Falta archivo destino.")
            elif cmd == "clear" or cmd == "cls":
                # Flushear el buffer completo de la consola
                output_txt.configure(state="normal")
                output_txt.delete("1.0", "end")
                output_txt.configure(state="disabled")
            elif cmd == "echo":
                log(" ".join(parts[1:]))
            elif cmd == "date":
                log("RTC System Clock: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            elif cmd == "exit":
                win.close_window() # Despacha orden de matar el proceso a la GUI
            else:
                log(f"Bash/CMD Panic: '{cmd}' es un opcode no registrado en este núcleo.")
            log("")
            
        cmd_entry.bind("<Return>", execute_command) # Interceptar pulsación 'Enter' para correr parseo

# ==============================================================================
# ENTRY POINT PRINCIPAL (PUNTO DE ARRANQUE DEL BOOTLOADER)
# ==============================================================================
if __name__ == "__main__":
    import sys
    
    # Flags de Comandos: Permiten arrancar módulos satélites de forma aislada
    
    if len(sys.argv) > 1 and sys.argv[1] == "--pyqt-browser":
        # Launch PyQt6 Browser
        import browser_engine
        app = browser_engine.QApplication(sys.argv)
        window = browser_engine.Browser("https://duckduckgo.com")
        window.show()
        sys.exit(app.exec())
        
    if len(sys.argv) > 1 and sys.argv[1] == "--browser":
        # Alternativa legacy webview
        import webview
        url = sys.argv[2] if len(sys.argv) > 2 else "https://www.google.com"
        webview.create_window("Navegador Web - Núcleo Externo", url, width=1200, height=800)
        webview.start()
        sys.exit(0)

    # El Arranque Genuino (Instanciación del Kernel principal)
    app = MiniWindowsV4()
    app.mainloop() # Inicio infinito del Event Loop de Tkinter
