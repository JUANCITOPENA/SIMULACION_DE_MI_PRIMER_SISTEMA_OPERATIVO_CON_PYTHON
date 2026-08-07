import customtkinter as ctk
import datetime
import os
import json
import psutil
import cv2
import pygame
import threading
from tkinter import messagebox, simpledialog, filedialog
from tkinterweb import HtmlFrame
from tkcalendar import Calendar
from PIL import Image, ImageTk, ImageOps
import moviepy as mp

# Inicializar Pygame Mixer
pygame.mixer.init()

# Configuración Global
BASE_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "SISTEMAS OPERATIVOS")
ROOT_DIR = os.path.join(BASE_PATH, "VIRTUAL_DRIVE")
TEMP_DIR = os.path.join(BASE_PATH, "temp")
if not os.path.exists(ROOT_DIR): os.makedirs(ROOT_DIR)
if not os.path.exists(TEMP_DIR): os.makedirs(TEMP_DIR)

THEMES = {
    "Windows 11": ["#0078d4", "#2b88d8", "#202020", "white", "dark"],
    "Dark Cobalt": ["#1e3799", "#4a69bd", "#0c2461", "white", "dark"],
    "Emerald": ["#079992", "#38ada9", "#006266", "white", "dark"],
    "Sunset": ["#e55039", "#eb2f06", "#b71540", "white", "dark"],
    "Minimal White": ["#636e72", "#b2bec3", "#ffffff", "black", "light"]
}

class InternalWindow(ctk.CTkFrame):
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, on_minimize=None, theme_colors=None, **kwargs):
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        title_bg = theme_colors[0] if theme_colors else "#34495e"
        text_col = theme_colors[3] if theme_colors else "white"
        
        super().__init__(master, width=width, height=height, corner_radius=10, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self.app_id = app_id
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.is_maximized = False
        self.old_geometry = {"x": 300, "y": 100, "w": width, "h": height}
        
        self.title_bar = ctk.CTkFrame(self, height=35, fg_color=title_bg, corner_radius=10)
        self.title_bar.pack(fill="x", side="top", padx=2, pady=2)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"), text_color=text_col)
        self.title_label.pack(side="left", padx=10)
        
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, text_color=text_col, fg_color="#e81123", hover_color="#f1707a", command=self.close_window)
        self.close_btn.pack(side="right", padx=2)
        
        self.max_btn = ctk.CTkButton(self.title_bar, text="□", width=30, height=25, text_color=text_col, fg_color="transparent", hover_color="#555555", command=self.toggle_maximize)
        self.max_btn.pack(side="right", padx=2)
        
        self.min_btn = ctk.CTkButton(self.title_bar, text="_", width=30, height=25, text_color=text_col, fg_color="transparent", hover_color="#555555", command=self.minimize_window)
        self.min_btn.pack(side="right", padx=2)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        self.content.pack_propagate(False)
        
        self.grip = ctk.CTkFrame(self, width=20, height=20, fg_color="transparent", cursor="sizing")
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<B1-Motion>", self.do_resize)
        
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.bind("<Button-1>", lambda e: self.lift())

        self._resize_job = None

    def start_drag(self, event):
        if self.is_maximized: return
        self._drag_data = {"x": event.x, "y": event.y}
        self.lift()

    def do_drag(self, event):
        if self.is_maximized: return
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.place(x=x, y=y)
        
    def do_resize(self, event):
        if self.is_maximized: return
        new_w = max(200, event.x_root - self.winfo_rootx())
        new_h = max(150, event.y_root - self.winfo_rooty())
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(30, lambda: self._apply_resize(new_w, new_h))
        
    def _apply_resize(self, w, h):
        self.configure(width=w, height=h)
        self.place(width=w, height=h)

    def toggle_maximize(self):
        if not self.is_maximized:
            self.old_geometry = {"x": self.winfo_x(), "y": self.winfo_y(), "w": self.winfo_width(), "h": self.winfo_height()}
            parent = self.master
            self.place(x=0, y=0, width=parent.winfo_width(), height=parent.winfo_height())
            self.is_maximized = True
            self.grip.place_forget()
        else:
            self.place(x=self.old_geometry["x"], y=self.old_geometry["y"], width=self.old_geometry["w"], height=self.old_geometry["h"])
            self.is_maximized = False
            self.grip.place(relx=1.0, rely=1.0, anchor="se")

    def minimize_window(self):
        if self.on_minimize: self.on_minimize(self.app_id)
        self.place_forget()

    def close_window(self):
        if self.on_close: self.on_close(self.app_id)
        self.destroy()

class MiniWindowsV4(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mini Windows JPV v4.2 - Multimedia Pro")
        self.geometry("1300x850")
        
        self.wallpapers = self.scan_wallpapers()
        self.load_settings()
        self.running_apps = {}
        
        # Check index valid
        if self.current_wallpaper_idx >= len(self.wallpapers):
            self.current_wallpaper_idx = 0

        # Desktop
        self.desktop = ctk.CTkFrame(self, corner_radius=0)
        self.desktop.pack(fill="both", expand=True)
        
        self.bg_label = ctk.CTkLabel(self.desktop, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", lambda e: self.load_wallpaper())
        
        # Taskbar
        self.taskbar = ctk.CTkFrame(self, height=55, fg_color=("#dfe6e9", "#2d3436"), corner_radius=0)
        self.taskbar.pack(side="bottom", fill="x")

        # Botones Taskbar
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
        
        self.apps_tb_frame = ctk.CTkScrollableFrame(self.taskbar, fg_color="transparent", orientation="horizontal", height=45)
        self.apps_tb_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        self.vol_frame = ctk.CTkFrame(self.taskbar, fg_color="transparent")
        self.vol_frame.pack(side="right", padx=20)
        self.vol_label = ctk.CTkLabel(self.vol_frame, text="🔊", font=("Segoe UI", 14))
        self.vol_label.pack(side="left", padx=5)
        self.vol_slider = ctk.CTkSlider(self.vol_frame, from_=0, to=1, width=100, command=self.change_volume)
        self.vol_slider.set(1.0); self.vol_slider.pack(side="left")

        self.clock_btn = ctk.CTkButton(self.taskbar, text="", font=("Consolas", 12, "bold"),
                                        fg_color="transparent", width=180, command=self.open_calendar)
        self.clock_btn.pack(side="right", padx=10)
        
        self.update_time()
        self.setup_desktop_icons()
        self.start_menu = None
        self.context_menu = None
        self.load_wallpaper()
        
        self.bg_label.bind("<Button-1>", self.on_desktop_click)
        self.bg_label.bind("<Button-3>", self.show_context_menu)


    def load_settings(self):
        self.settings_file = os.path.join(ROOT_DIR, "settings.json")
        default_settings = {"theme": "Windows 11", "wallpaper_idx": 0, "volume": 1.0, "installed_apps": []}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    default_settings.update(data)
            except: pass
        self.current_theme = default_settings["theme"]
        self.current_wallpaper_idx = default_settings["wallpaper_idx"]
        self.volume_level = default_settings["volume"]
        self.installed_apps = default_settings["installed_apps"]

    def save_settings(self):
        data = {
            "theme": self.current_theme,
            "wallpaper_idx": self.current_wallpaper_idx,
            "volume": getattr(self, "volume_level", 1.0),
            "installed_apps": getattr(self, "installed_apps", [])
        }
        try:
            with open(self.settings_file, "w") as f:
                json.dump(data, f)
        except Exception as e: print(f"Error saving settings: {e}")

    def get_wallpaper_dir(self):
        wall_dir = os.path.join(BASE_PATH, "assets", "wallpapers")
        os.makedirs(wall_dir, exist_ok=True)
        return wall_dir

    def scan_wallpapers(self):
        wall_dir = self.get_wallpaper_dir()
        # Migrar fondos antiguos
        old_ws = [f for f in os.listdir(BASE_PATH) if f.lower().startswith("fondo") and f.lower().endswith((".png", ".jpg", ".jpeg"))]
        import shutil
        for old_w in old_ws:
            try: shutil.move(os.path.join(BASE_PATH, old_w), os.path.join(wall_dir, old_w))
            except: pass
            
        ws = [f for f in os.listdir(wall_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not ws:
            img = Image.new('RGB', (1920, 1080), color = '#2c3e50')
            img.save(os.path.join(wall_dir, "default.png"))
            ws = ["default.png"]
        return sorted(ws)

    def load_wallpaper(self):
        try:
            fname = self.wallpapers[self.current_wallpaper_idx]
            path = os.path.join(self.get_wallpaper_dir(), fname)
            if not os.path.exists(path): return
            
            wall_img = Image.open(path)
            # AJUSTE PROPORCIONAL (NO DISTORSIÓN)
            win_w = self.desktop.winfo_width()
            win_h = self.desktop.winfo_height()
            if win_w < 100 or win_h < 100: win_w, win_h = 1300, 850
            
            wall_img = ImageOps.fit(wall_img, (win_w, win_h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            self.bg_image = ctk.CTkImage(wall_img, wall_img, size=(win_w, win_h))
            self.bg_label.configure(image=self.bg_image)
        except Exception as e: print(f"Error wallpaper: {e}")

    def change_wallpaper(self):
        self.current_wallpaper_idx = (self.current_wallpaper_idx + 1) % len(self.wallpapers)
        self.load_wallpaper()

    def change_volume(self, value):
        self.volume_level = float(value)
        pygame.mixer.music.set_volume(self.volume_level)
        icon = "🔇" if self.volume_level == 0 else "🔉" if self.volume_level < 0.5 else "🔊"
        self.vol_label.configure(text=icon)
        self.save_settings()

    def update_time(self):
        self.clock_btn.configure(text=datetime.datetime.now().strftime("%I:%M:%S %p\n%d/%m/%Y"))
        self.after(1000, self.update_time)

    def apply_theme(self, name):
        self.current_theme = name
        colors = THEMES[name]
        ctk.set_appearance_mode(colors[4])
        self.start_btn.configure(fg_color=colors[0], hover_color=colors[1])
        # Actualizar color texto iconos
        txt_col = "white" if colors[4] == "dark" else "black"
        for child in self.desktop.winfo_children():
            if isinstance(child, ctk.CTkButton) and child != self.bg_label:
                child.configure(text_color=txt_col)
        messagebox.showinfo("Sistema", f"Tema '{name}' aplicado.")
        self.save_settings()

    def setup_desktop_icons(self):
        self.icon_images = getattr(self, "icon_images", {})
        icon_data = [
            ("Mi PC", "mypc", self.open_my_pc, "mypc.png"),
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
        y_pos = 30
        x_pos = 40
        # Limpiar iconos anteriores si existen
        for widget in self.desktop.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()

        # Renderizar iconos fijos
        for i, (name, aid, cmd, icon_file) in enumerate(icon_data):
            img_path = os.path.join(assets_dir, icon_file)
            img = None
            if os.path.exists(img_path):
                img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                self.icon_images[aid] = img
            
            btn = ctk.CTkButton(self.desktop, text=name, image=img, compound="top", width=100, height=90, text_color=("#000000", "#FFFFFF"), 
                                 fg_color="transparent", 
                                 hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 13, "bold"), command=cmd)
            btn.place(x=x_pos, y=y_pos)
            y_pos += 110
            if y_pos > 600:
                y_pos = 30
                x_pos += 120

        # Renderizar carpetas y archivos creados por el usuario en el escritorio
        if os.path.exists(ROOT_DIR):
            for item in os.listdir(ROOT_DIR):
                if item == "settings.json": continue
                item_path = os.path.join(ROOT_DIR, item)
                is_dir = os.path.isdir(item_path)
                
                # Reutilizamos los iconos existentes si podemos
                fallback_icon = "explorer.png" if is_dir else "notepad.png"
                img_path = os.path.join(assets_dir, fallback_icon)
                img = None
                if os.path.exists(img_path):
                    img = ctk.CTkImage(light_image=Image.open(img_path), size=(50, 50))
                    self.icon_images[item] = img
                    
                # Definimos una acción al hacer clic: Abrir el explorador o el bloc de notas
                if is_dir:
                    action = self.open_explorer
                else:
                    action = self.open_notepad
                    
                btn = ctk.CTkButton(self.desktop, text=item[:10], image=img, compound="top", width=100, height=90, text_color=("#000000", "#FFFFFF"), 
                                     fg_color="transparent", 
                                     hover_color=("#b2bec3", "#636e72"), font=("Segoe UI", 12), command=action)
                btn.place(x=x_pos, y=y_pos)
                y_pos += 110
                if y_pos > 600:
                    y_pos = 30
                    x_pos += 120


    def toggle_start_menu(self):
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        else:
            if self.context_menu: self.context_menu.destroy(); self.context_menu = None
            self.start_menu = ctk.CTkFrame(self.desktop, width=350, height=600, border_width=2, corner_radius=20)
            self.start_menu.pack_propagate(False)
            self.start_menu.place(x=10, y=self.desktop.winfo_height() - 610); self.start_menu.lift()
            
            ctk.CTkLabel(self.start_menu, text="SISTEMA JPV v4.2", font=("Segoe UI", 20, "bold")).pack(pady=20)
            
            scroll_f = ctk.CTkScrollableFrame(self.start_menu, fg_color="transparent")
            scroll_f.pack(fill="both", expand=True, padx=10, pady=5)
            
            apps = [("🗂️ Explorador", self.open_explorer), ("🌍 Navegador", self.open_browser), ("📽️ Video Player", self.open_video_player),
                    ("🖥️ Mi PC", self.open_my_pc), ("🗒️ Notepad", self.open_notepad), ("🧮 Calculadora", self.open_calc),
                    ("⚙️ Configuración", self.open_control_panel), ("📊 Task Manager", self.open_task_manager), ("💻 Terminal", self.open_terminal), ("🛒 App Store", self.open_app_store)]
            
            for n, c in apps:
                ctk.CTkButton(scroll_f, text=n, fg_color="transparent", text_color=("#000000", "#FFFFFF"), anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            
            ctk.CTkLabel(scroll_f, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=10)
            
            for tname in THEMES:
                ctk.CTkButton(scroll_f, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=20, pady=2)
            
            ctk.CTkButton(scroll_f, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=20, pady=15)

    def request_app(self, app_id, title, size):
        if app_id in self.running_apps:
            self.restore_app(app_id)
            return None
        win = InternalWindow(self.desktop, app_id, title, *map(int, size.split('x')), 
                             on_close=self.on_app_close, on_minimize=self.on_app_minimize, theme_colors=THEMES[self.current_theme])
        self.running_apps[app_id] = win
        win.place(x=300, y=100)
        self.update_taskbar_buttons()
        return win

    def on_app_close(self, app_id):
        if app_id in self.running_apps: 
            del self.running_apps[app_id]
            self.update_taskbar_buttons()

    def on_desktop_click(self, event):
        if getattr(self, "start_menu", None): self.start_menu.destroy(); self.start_menu = None
        if getattr(self, "context_menu", None): self.context_menu.destroy(); self.context_menu = None

    def show_context_menu(self, event):
        self.on_desktop_click(None)
        self.context_menu = ctk.CTkFrame(self.desktop, width=150, corner_radius=5, border_width=1, border_color="gray")
        self.context_menu.place(x=event.x, y=event.y)
        
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
                          
    def show_internal_input_dialog(self, title, prompt, on_submit):
        # Cuadro de dialogo totalmente interno al sistema simulado
        dialog = ctk.CTkFrame(self.desktop, width=320, height=160, corner_radius=15, border_width=2, border_color="gray", fg_color=("#ecf0f1", "#2c3e50"))
        dialog.place(relx=0.5, rely=0.5, anchor="center")
        dialog.pack_propagate(False)
        dialog.lift()

        ctk.CTkLabel(dialog, text=title, font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(dialog, text=prompt, font=("Segoe UI", 12)).pack()
        
        entry = ctk.CTkEntry(dialog, width=260)
        entry.pack(pady=10)
        entry.focus_set()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        def submit(event=None):
            val = entry.get()
            dialog.destroy()
            if val: on_submit(val)
                
        def cancel():
            dialog.destroy()
            
        ctk.CTkButton(btn_frame, text="Aceptar", width=100, command=submit).pack(side="left", padx=25)
        ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="#e81123", hover_color="#f1707a", command=cancel).pack(side="right", padx=25)
        
        entry.bind("<Return>", submit)

    def refresh_desktop(self):
        # Oculta temporalmente los iconos para simular el parpadeo del refresco de Windows real
        for widget in self.desktop.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget != self.bg_label:
                widget.place_forget()
        self.update()
        self.after(250, lambda: [self.load_wallpaper(), self.setup_desktop_icons()])

    def create_new_folder(self):
        def on_submit(name):
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            self.setup_desktop_icons()
        self.show_internal_input_dialog("Nueva Carpeta", "Nombre de la carpeta:", on_submit)
            
    def create_new_file(self):
        def on_submit(name):
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("")
            self.setup_desktop_icons()
        self.show_internal_input_dialog("Nuevo Archivo", "Nombre del archivo (ej. notas.txt):", on_submit)

    def update_taskbar_buttons(self):
        for widget in self.apps_tb_frame.winfo_children():
            widget.destroy()
            
        for app_id, win in self.running_apps.items():
            btn = ctk.CTkButton(self.apps_tb_frame, text=win.title_label.cget("text"), width=120, height=30,
                                fg_color="transparent", text_color=("#000000", "#FFFFFF"), border_width=1, border_color="gray",
                                hover_color="#555555", command=lambda aid=app_id: self.restore_app(aid))
            btn.pack(side="left", padx=5)

    def restore_app(self, app_id):
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            if not win.winfo_viewable():
                win.place(x=win.old_geometry.get("x", 300), y=win.old_geometry.get("y", 100), 
                          width=win.old_geometry.get("w", win.winfo_width()), height=win.old_geometry.get("h", win.winfo_height()))
            win.lift()

    def on_app_minimize(self, app_id):
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            win.old_geometry = {"x": win.winfo_x(), "y": win.winfo_y(), "w": win.winfo_width(), "h": win.winfo_height()}

    # --- VIDEO PLAYER PRO (AUDIO REAL + SIN DISTORSIÓN) ---
    def open_video_player(self):
        win = self.request_app("video", "JPV Video Pro (Audio+)", "800x650")
        if not win: return
        vpath = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.avi")])
        if not vpath: win.destroy(); return
        
        # Extraer Audio con MoviePy
        audio_temp = os.path.join(TEMP_DIR, "temp_audio.mp3")
        def extract():
            try:
                clip = mp.VideoFileClip(vpath)
                clip.audio.write_audiofile(audio_temp, logger=None)
                pygame.mixer.music.load(audio_temp)
                pygame.mixer.music.play()
            except: pass
        threading.Thread(target=extract, daemon=True).start()

        cap = cv2.VideoCapture(vpath)
        total_f = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        canvas = ctk.CTkLabel(win.content, text="")
        canvas.pack(fill="both", expand=True)
        
        seek = ctk.CTkSlider(win.content, from_=0, to=total_f, height=15, command=lambda v: [cap.set(cv2.CAP_PROP_POS_FRAMES, int(v)), pygame.mixer.music.play(start=int(v)/cap.get(cv2.CAP_PROP_FPS))])
        seek.pack(fill="x", pady=5)
        
        self.is_playing = True
        def toggle():
            self.is_playing = not self.is_playing
            if self.is_playing: pygame.mixer.music.unpause()
            else: pygame.mixer.music.pause()

        ctk.CTkButton(win.content, text="Play/Pausa", command=toggle).pack(pady=5)

        def stream():
            if not win.winfo_exists(): 
                cap.release(); pygame.mixer.music.stop(); return
            if self.is_playing:
                ret, frame = cap.read()
                if ret:
                    seek.set(int(cap.get(cv2.CAP_PROP_POS_FRAMES)))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Mantener Aspect Ratio en Video
                    img = Image.fromarray(frame)
                    img = ImageOps.contain(img, (750, 450))
                    imgtk = ImageTk.PhotoImage(image=img)
                    canvas.imgtk = imgtk; canvas.configure(image=imgtk)
            win.after(25, stream)
        stream()

    # --- OTRAS APPS ---
    def open_explorer(self, path=ROOT_DIR):
        win = self.request_app("explorer", f"Explorador - {os.path.basename(path) or 'Raíz'}", "700x500")
        if not win: return
        nav = ctk.CTkFrame(win.content, height=40); nav.pack(fill="x", pady=2)
        ctk.CTkButton(nav, text="⬆️ Subir", width=70, command=lambda: [win.destroy(), self.on_app_close("explorer"), self.open_explorer(os.path.dirname(path))]).pack(side="left", padx=5)
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True)
        for item in os.listdir(path):
            fp = os.path.join(path, item); is_d = os.path.isdir(fp)
            ctk.CTkButton(scroll, text=f"{'📁' if is_d else '📄'} {item}", anchor="w", fg_color="transparent", text_color=("#000000", "#FFFFFF"), command=lambda p=fp: [win.destroy(), self.on_app_close("explorer"), self.open_explorer(p)] if os.path.isdir(p) else self.open_notepad(p)).pack(fill="x")

    def open_browser(self):
        # Lanzar el navegador PyQt6 directamente sin interfaz intermedia
        import subprocess, sys
        subprocess.Popen([sys.executable, "--pyqt-browser"])

    def open_my_pc(self):
        win = self.request_app("mypc", "Mi PC", "650x550")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Seccion 1: Carpetas Frecuentes
        ctk.CTkLabel(scroll, text="Carpetas Principales", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(0, 10))
        folders_f = ctk.CTkFrame(scroll, fg_color="transparent")
        folders_f.pack(fill="x")
        
        folders = [("Desktop", "Escritorio"), ("Downloads", "Descargas"), ("Documents", "Documentos"), ("Pictures", "Imágenes")]
        for i, (f_icon, f_name) in enumerate(folders):
            folder_path = ROOT_DIR if f_icon == "Desktop" else os.path.join(ROOT_DIR, f_name)
            os.makedirs(folder_path, exist_ok=True)
            
            btn = ctk.CTkButton(folders_f, text=f"📁 {f_name}", width=120, height=40, fg_color=("#dfe6e9", "#2d3436"), hover_color="#555555", text_color=("#000000", "#FFFFFF"),
                                command=lambda path=folder_path: [win.destroy(), self.on_app_close("mypc"), self.open_explorer(path)])
            btn.grid(row=0, column=i, padx=10, pady=5)
        self.setup_desktop_icons()
            
        # Seccion 2: Discos Duros
        ctk.CTkLabel(scroll, text="Dispositivos y unidades", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", pady=(20, 10))
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
                f.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(f, text="💾", font=("Segoe UI", 28)).pack(side="left", padx=20, pady=10)
                
                info = ctk.CTkFrame(f, fg_color="transparent")
                info.pack(side="left", fill="both", expand=True, pady=10)
                
                ctk.CTkLabel(info, text=f"Disco Local ({p.device[:2]})", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")
                pg = ctk.CTkProgressBar(info, height=12, progress_color="#0984e3")
                pg.pack(fill="x", pady=5, padx=5)
                pg.set(u.percent/100)
                ctk.CTkLabel(info, text=f"{u.free//2**30} GB disponibles de {u.total//2**30} GB", font=("Segoe UI", 11), text_color=("#444444", "#AAAAAA"), anchor="w").pack(fill="x")
            except: continue

    def open_notepad(self, path=None):
        win = self.request_app("notepad", "Notepad JPV", "600x500")
        if not win: return
        txt = ctk.CTkTextbox(win.content, font=("Consolas", 14)); txt.pack(fill="both", expand=True)
        if path:
            with open(path, "r") as f: txt.insert("0.0", f.read())
        def save():
            p = path or filedialog.asksaveasfilename(initialdir=ROOT_DIR, defaultextension=".txt")
            if p:
                with open(p, "w") as f: f.write(txt.get("0.0", "end"))
                messagebox.showinfo("Sistema", "Guardado."); win.destroy(); self.on_app_close("notepad")
        ctk.CTkButton(win.content, text="💾 Guardar", command=save, fg_color="#00b894").pack(pady=10)

    def open_calc(self):
        win = self.request_app("calc", "Calculadora", "320x450")
        if not win: return
        ent = ctk.CTkEntry(win.content, font=("Consolas", 24), justify="right"); ent.pack(fill="x", padx=10, pady=15)
        grid = ctk.CTkFrame(win.content); grid.pack(fill="both", expand=True)
        btns = ['7','8','9','/','4','5','6','*','1','2','3','-','C','0','=','+']
        r, c = 0, 0
        for b in btns:
            ctk.CTkButton(grid, text=b, width=65, height=65, text_color=("#000000", "#FFFFFF"), command=lambda x=b: [ent.insert("end", x) if x not in ["=","C"] else (ent.delete(0,"end") if x=="C" else ent.insert("end","="+str(eval(ent.get()))))]).grid(row=r, column=c, padx=3, pady=3)
            c+=1; 
            if c>3: c=0; r+=1

    def open_calendar(self):
        win = self.request_app("calendar", "Calendario", "400x500")
        if not win: return
        Calendar(win.content).pack(pady=10, padx=10, fill="both", expand=True)



    def open_wallpaper_selector(self):
        win = self.request_app("wallpapers", "Fondos de Pantalla", "600x450")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        wall_dir = self.get_wallpaper_dir()
        ctk.CTkLabel(scroll, text=f"Directorio de imágenes:\\n{wall_dir}", font=("Segoe UI", 12), text_color=("#444444", "#AAAAAA")).pack(pady=(0,10))
        
        grid_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        
        row, col = 0, 0
        for idx, w in enumerate(self.wallpapers):
            path = os.path.join(wall_dir, w)
            if os.path.exists(path):
                try:
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
        win = self.request_app("settings", "Panel de Control", "600x450")
        if not win: return
        ctk.CTkLabel(win.content, text="⚙️ Configuración del Sistema", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        f_tema = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
        f_tema.pack(fill="x", pady=10)
        ctk.CTkLabel(f_tema, text="🎨 Apariencia y Temas", font=("Segoe UI", 16, "bold")).pack(pady=5)
        themes_frame = ctk.CTkFrame(f_tema, fg_color="transparent")
        themes_frame.pack(pady=10)
        for tname in THEMES:
            ctk.CTkButton(themes_frame, text=tname, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(side="left", padx=5)
            
        f_sys = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
        f_sys.pack(fill="x", pady=10)
        ctk.CTkLabel(f_sys, text="💻 Información del Sistema (Real)", font=("Segoe UI", 16, "bold")).pack(pady=5)
        ram = psutil.virtual_memory()
        ctk.CTkLabel(f_sys, text=f"Memoria RAM Total: {ram.total // (1024**3)} GB", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(f_sys, text=f"Memoria RAM en Uso: {ram.percent}%", font=("Segoe UI", 14)).pack()
        ctk.CTkLabel(f_sys, text=f"Uso de CPU Actual: {psutil.cpu_percent()}%", font=("Segoe UI", 14)).pack(pady=(0, 10))

    def open_task_manager(self):
        win = self.request_app("taskmgr", "Administrador de Tareas", "400x500")
        if not win: return
        ctk.CTkLabel(win.content, text="📋 Procesos Activos (JPV OS)", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        self.task_list_frame = ctk.CTkScrollableFrame(win.content)
        self.task_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.task_widgets = {} # Guarda ref a frames existentes
        
        def refresh_tasks():
            if not win.winfo_exists(): return
            
            # Borrar procesos que ya no existen
            current_apps = list(self.running_apps.keys())
            for tid in list(self.task_widgets.keys()):
                if tid not in current_apps:
                    self.task_widgets[tid].destroy()
                    del self.task_widgets[tid]
            
            # Añadir procesos nuevos
            for app_id, app_win in list(self.running_apps.items()):
                if app_id not in self.task_widgets:
                    f = ctk.CTkFrame(self.task_list_frame, fg_color=("#dfe6e9", "#2d3436"), corner_radius=5)
                    f.pack(fill="x", pady=2)
                    ctk.CTkLabel(f, text=app_win.title_label.cget("text")).pack(side="left", padx=10, pady=5)
                    ctk.CTkButton(f, text="Finalizar", fg_color="#e17055", hover_color="#d63031", width=60, height=24,
                                  command=lambda aid=app_id: self.running_apps[aid].close_window() if aid in self.running_apps else None).pack(side="right", padx=10)
                    self.task_widgets[app_id] = f
            
            win.after(2000, refresh_tasks)
            
        refresh_tasks()

    def open_app_store(self):
        win = self.request_app("store", "JPV App Store", "600x450")
        if not win: return
        
        ctk.CTkLabel(win.content, text="🛒 Centro de Descargas", font=("Segoe UI", 24, "bold")).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        apps_disp = [
            ("Snake Game", "Un clásico juego de la serpiente.", "snake"),
            ("WordPad Pro", "Editor avanzado con formato RTF.", "wordpad"),
            ("Calculadora Científica", "Matemáticas avanzadas.", "calc_pro")
        ]
        
        def download_app(app_id, btn, bar):
            btn.configure(state="disabled", text="Descargando...")
            
            def finish():
                btn.configure(text="¡Instalado!", fg_color="green")
                if app_id not in self.installed_apps:
                    self.installed_apps.append(app_id)
                    self.save_settings()
                messagebox.showinfo("Instalación Completada", f"Aplicación {app_id} instalada en tu sistema.")
            
            # Simulación de descarga
            def step(progress=0.0):
                if progress >= 1.0: finish(); return
                bar.set(progress)
                win.after(100, lambda: step(progress + 0.05))
                
            step()

        for name, desc, appid in apps_disp:
            f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10)
            f.pack(fill="x", pady=10)
            
            info_f = ctk.CTkFrame(f, fg_color="transparent")
            info_f.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            ctk.CTkLabel(info_f, text=name, font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x")
            ctk.CTkLabel(info_f, text=desc, font=("Segoe UI", 12), anchor="w").pack(fill="x")
            
            bar = ctk.CTkProgressBar(f, width=100)
            bar.pack(side="left", padx=10)
            bar.set(0)
            
            btn = ctk.CTkButton(f, text="Instalado" if appid in getattr(self, 'installed_apps', []) else "Descargar", text_color=("#000000", "#FFFFFF"), 
                                width=90, fg_color="green" if appid in getattr(self, 'installed_apps', []) else "#0984e3",
                                state="disabled" if appid in getattr(self, 'installed_apps', []) else "normal")
            btn.configure(command=lambda aid=appid, b=btn, br=bar: download_app(aid, b, br))
            btn.pack(side="right", padx=15, pady=15)


    def open_terminal(self):
        win = self.request_app("terminal", "JPV Terminal", "600x400")
        if not win: return
        win.content.configure(fg_color="black")
        
        output_txt = ctk.CTkTextbox(win.content, fg_color="black", text_color="#00ff00", font=("Consolas", 14), state="disabled")
        output_txt.pack(fill="both", expand=True, padx=5, pady=5)
        
        input_frame = ctk.CTkFrame(win.content, fg_color="black")
        input_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(input_frame, text="C:\\VIRTUAL_DRIVE> ", text_color="#00ff00", font=("Consolas", 14)).pack(side="left")
        
        cmd_var = ctk.StringVar()
        cmd_entry = ctk.CTkEntry(input_frame, textvariable=cmd_var, fg_color="black", text_color="#00ff00", border_width=0, font=("Consolas", 14))
        cmd_entry.pack(side="left", fill="x", expand=True)
        cmd_entry.focus()
        
        self.current_term_dir = ROOT_DIR
        
        def log(text):
            output_txt.configure(state="normal")
            output_txt.insert("end", text + "\n")
            output_txt.configure(state="disabled")
            output_txt.see("end")

        log("Mini Windows JPV Terminal [Versión 2.0]")
        log("(c) Ing. Juancito Peña. Todos los derechos reservados.\n")
        
        def execute_command(event=None):
            command = cmd_var.get().strip()
            if not command: return
            
            cmd_var.set("")
            log(f"C:\\VIRTUAL_DRIVE> {command}")
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == "help":
                log("Comandos disponibles: help, dir, clear, echo, date, exit")
            elif cmd == "dir":
                try:
                    for item in os.listdir(self.current_term_dir):
                        log(f"  {item}")
                except Exception as e:
                    log(f"Error: {e}")
            elif cmd == "clear":
                output_txt.configure(state="normal")
                output_txt.delete("1.0", "end")
                output_txt.configure(state="disabled")
            elif cmd == "echo":
                log(" ".join(parts[1:]))
            elif cmd == "date":
                log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            elif cmd == "exit":
                win.close_window()
            else:
                log(f"'{cmd}' no se reconoce como un comando interno o externo.")
            log("")
            
        cmd_entry.bind("<Return>", execute_command)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--pyqt-browser":
        # Launch PyQt6 Browser
        import browser_engine
        app = browser_engine.QApplication(sys.argv)
        window = browser_engine.Browser("https://www.google.com")
        window.show()
        sys.exit(app.exec())
        
    if len(sys.argv) > 1 and sys.argv[1] == "--browser":
        import webview
        url = sys.argv[2] if len(sys.argv) > 2 else "https://www.google.com"
        webview.create_window("Navegador Web - Mini Windows", url, width=1200, height=800)
        webview.start()
        sys.exit(0)

    app = MiniWindowsV4()
    app.mainloop()
