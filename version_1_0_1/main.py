import sys

# --- PARCHE DE INGENIERÍA PARA PYINSTALLER (IMAGEIO METADATA FIX) ---
if hasattr(sys, '_MEIPASS'):
    import importlib.metadata
    _original_version = importlib.metadata.version
    def _patched_version(package_name):
        if package_name == 'imageio': return "2.37.3"
        if package_name == 'moviepy': return "2.1.1"
        return _original_version(package_name)
    importlib.metadata.version = _patched_version

import customtkinter as ctk
import datetime
import os
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
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, theme_colors=None, **kwargs):
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        super().__init__(master, width=width, height=height, corner_radius=15, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        self.app_id = app_id
        self.on_close = on_close

        # Barra de Título
        self.title_bar = ctk.CTkFrame(self, height=40, fg_color="#34495e", corner_radius=12)
        self.title_bar.pack(fill="x", side="top", padx=3, pady=3)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=15)
        
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=35, height=30, 
                                        fg_color="#e17055", hover_color="#d63031", command=self.close_window)
        self.close_btn.pack(side="right", padx=5)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.bind("<Button-1>", lambda e: self.lift())

    def start_drag(self, event):
        self._drag_data = {"x": event.x, "y": event.y}
        self.lift()

    def do_drag(self, event):
        x = self.winfo_x() - self._drag_data["x"] + event.x
        y = self.winfo_y() - self._drag_data["y"] + event.y
        self.place(x=x, y=y)

    def close_window(self):
        if self.on_close: self.on_close(self.app_id)
        self.destroy()

class MiniWindowsV4(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mini Windows JPV v4.2 - Multimedia Pro")
        self.geometry("1300x850")
        
        self.current_theme = "Windows 11"
        self.running_apps = {}
        self.wallpapers = self.scan_wallpapers()
        self.current_wallpaper_idx = 0
        self.volume_level = 1.0

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
        self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=60, height=45,
                                        fg_color=THEMES[self.current_theme][0], 
                                        command=self.toggle_start_menu)
        self.start_btn.pack(side="left", padx=15, pady=5)

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
        self.load_wallpaper()

    def scan_wallpapers(self):
        ws = [f for f in os.listdir(BASE_PATH) if f.lower().startswith("fondo") and f.lower().endswith((".png", ".jpg", ".jpeg"))]
        return sorted(ws) if ws else ["fondo.png"]

    def load_wallpaper(self):
        try:
            fname = self.wallpapers[self.current_wallpaper_idx]
            path = os.path.join(BASE_PATH, fname)
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

    def setup_desktop_icons(self):
        icons = [("💻 Mi PC", "mypc", self.open_my_pc), ("📂 Explorador", "explorer", self.open_explorer),
                 ("🌐 Navegador", "browser", self.open_browser), ("🎬 Video Pro", "video", self.open_video_player),
                 ("📝 Notepad", "notepad", self.open_notepad)]
        for i, (name, aid, cmd) in enumerate(icons):
            btn = ctk.CTkButton(self.desktop, text=name, width=100, height=110, fg_color="transparent", 
                                 text_color="white", hover_color=("#b2bec3", "#636e72"), 
                                 font=("Segoe UI", 12, "bold"), compound="top", command=cmd)
            btn.place(x=30, y=30 + (i * 125))

    def toggle_start_menu(self):
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        else:
            self.start_menu = ctk.CTkFrame(self.desktop, width=350, height=600, border_width=2, corner_radius=20)
            self.start_menu.place(x=10, y=self.desktop.winfo_height() - 610); self.start_menu.lift()
            ctk.CTkLabel(self.start_menu, text="SISTEMA JPV v4.2", font=("Segoe UI", 20, "bold")).pack(pady=20)
            app_f = ctk.CTkFrame(self.start_menu, fg_color="transparent"); app_f.pack(fill="both", expand=True, padx=10)
            apps = [("📂 Explorador", self.open_explorer), ("🌐 Navegador", self.open_browser), ("🎬 Video Player", self.open_video_player),
                    ("💻 Mi PC", self.open_my_pc), ("📝 Notepad", self.open_notepad), ("🧮 Calculadora", self.open_calc)]
            for n, c in apps:
                ctk.CTkButton(app_f, text=n, fg_color="transparent", anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            ctk.CTkLabel(self.start_menu, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=5)
            for tname in THEMES:
                ctk.CTkButton(self.start_menu, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=40, pady=1)
            ctk.CTkButton(self.start_menu, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=40, pady=10)

    def request_app(self, app_id, title, size):
        if app_id in self.running_apps:
            self.running_apps[app_id].lift(); return None
        win = InternalWindow(self.desktop, app_id, title, *map(int, size.split('x')), on_close=self.on_app_close, theme_colors=THEMES[self.current_theme])
        self.running_apps[app_id] = win
        win.place(x=300, y=100); return win

    def on_app_close(self, app_id):
        if app_id in self.running_apps: del self.running_apps[app_id]

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
            ctk.CTkButton(scroll, text=f"{'📁' if is_d else '📄'} {item}", anchor="w", fg_color="transparent", command=lambda p=fp: [win.destroy(), self.on_app_close("explorer"), self.open_explorer(p)] if os.path.isdir(p) else self.open_notepad(p)).pack(fill="x")

    def open_browser(self):
        win = self.request_app("browser", "JPV Browser", "950x700")
        if not win: return
        nav = ctk.CTkFrame(win.content, height=40); nav.pack(fill="x", side="top", pady=2)
        ent = ctk.CTkEntry(nav, placeholder_text="URL..."); ent.pack(side="left", fill="x", expand=True, padx=5)
        web = HtmlFrame(win.content); web.pack(fill="both", expand=True)
        ctk.CTkButton(nav, text="Ir", width=60, command=lambda: web.load_website(ent.get() if ent.get().startswith("http") else "https://"+ent.get())).pack(side="right", padx=5)
        web.load_website("https://www.google.com")

    def open_my_pc(self):
        win = self.request_app("mypc", "Mi PC - Estado", "600x450")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content); scroll.pack(fill="both", expand=True)
        for p in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(p.mountpoint)
                f = ctk.CTkFrame(scroll, fg_color=("#dfe6e9", "#34495e"), corner_radius=10); f.pack(fill="x", pady=5, padx=5)
                ctk.CTkLabel(f, text=f"Unidad {p.device}\n{u.free//2**30}GB Libres", justify="left").pack(side="left", padx=15, pady=10)
                pg = ctk.CTkProgressBar(f, width=180); pg.pack(side="right", padx=15); pg.set(u.percent/100)
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
            ctk.CTkButton(grid, text=b, width=65, height=65, command=lambda x=b: [ent.insert("end", x) if x not in ["=","C"] else (ent.delete(0,"end") if x=="C" else ent.insert("end","="+str(eval(ent.get()))))]).grid(row=r, column=c, padx=3, pady=3)
            c+=1; 
            if c>3: c=0; r+=1

    def open_calendar(self):
        win = self.request_app("calendar", "Calendario", "400x500")
        if not win: return
        Calendar(win.content).pack(pady=10, padx=10, fill="both", expand=True)

if __name__ == "__main__":
    app = MiniWindowsV4()
    app.mainloop()
