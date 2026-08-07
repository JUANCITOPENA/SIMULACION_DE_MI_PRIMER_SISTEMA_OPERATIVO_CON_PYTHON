import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add import json
if "import json" not in code:
    code = code.replace("import os", "import os\nimport json")

# 2. Add settings methods in MiniWindowsV4
settings_methods = """
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

"""
# Find __init__ of MiniWindowsV4 to insert load_settings
init_search = """        self.geometry("1300x850")
        
        self.current_theme = "Windows 11"
        self.running_apps = {}
        self.wallpapers = self.scan_wallpapers()
        self.current_wallpaper_idx = 0
        self.volume_level = 1.0"""
init_replace = """        self.geometry("1300x850")
        
        self.wallpapers = self.scan_wallpapers()
        self.load_settings()
        self.running_apps = {}
        
        # Check index valid
        if self.current_wallpaper_idx >= len(self.wallpapers):
            self.current_wallpaper_idx = 0"""

code = code.replace(init_search, init_replace)
code = code.replace("    def scan_wallpapers(self):", settings_methods + "    def scan_wallpapers(self):")

# 3. Update apply_theme, volume, wallpaper to save settings
code = code.replace('messagebox.showinfo("Sistema", f"Tema \'{name}\' aplicado.")', 'messagebox.showinfo("Sistema", f"Tema \'{name}\' aplicado.")\n        self.save_settings()')
code = code.replace('self.vol_label.configure(text=icon)', 'self.vol_label.configure(text=icon)\n        self.save_settings()')
code = code.replace("self.load_wallpaper()]).pack(fill=\"x\", pady=2)", "self.load_wallpaper(), self.save_settings()]).pack(fill=\"x\", pady=2)")

# 4. Modify App Store in desktop icons and start menu
old_desktop = """            ("Configuración", "settings", self.open_control_panel, "settings.png"),
            ("Task Mgr", "taskmgr", self.open_task_manager, "start.png"),
            ("Terminal", "terminal", self.open_terminal, "start.png")"""
new_desktop = """            ("Configuración", "settings", self.open_control_panel, "settings.png"),
            ("Task Mgr", "taskmgr", self.open_task_manager, "start.png"),
            ("Terminal", "terminal", self.open_terminal, "start.png"),
            ("App Store", "store", self.open_app_store, "explorer.png")"""
code = code.replace(old_desktop, new_desktop)

old_start = """                    ("⚙️ Configuración", self.open_control_panel), ("📊 Task Manager", self.open_task_manager), ("💻 Terminal", self.open_terminal)]"""
new_start = """                    ("⚙️ Configuración", self.open_control_panel), ("📊 Task Manager", self.open_task_manager), ("💻 Terminal", self.open_terminal), ("🛒 App Store", self.open_app_store)]"""
code = code.replace(old_start, new_start)


# 5. Fix Task Manager and Add App Store function
old_taskmgr = """    def open_task_manager(self):
        win = self.request_app("taskmgr", "Administrador de Tareas", "400x500")
        if not win: return
        ctk.CTkLabel(win.content, text="📋 Procesos Activos (JPV OS)", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        self.task_list_frame = ctk.CTkScrollableFrame(win.content)
        self.task_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        def refresh_tasks():
            if not win.winfo_exists(): return
            for widget in self.task_list_frame.winfo_children():
                widget.destroy()
            for app_id, app_win in list(self.running_apps.items()):
                f = ctk.CTkFrame(self.task_list_frame, fg_color=("#dfe6e9", "#2d3436"), corner_radius=5)
                f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=app_win.title_label.cget("text")).pack(side="left", padx=10, pady=5)
                ctk.CTkButton(f, text="Finalizar", fg_color="#e17055", hover_color="#d63031", width=60, height=24,
                              command=lambda aid=app_id: self.running_apps[aid].close_window()).pack(side="right", padx=10)
            win.after(2000, refresh_tasks)
            
        refresh_tasks()"""

new_taskmgr = """    def open_task_manager(self):
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
            
            btn = ctk.CTkButton(f, text="Instalado" if appid in getattr(self, 'installed_apps', []) else "Descargar", 
                                width=90, fg_color="green" if appid in getattr(self, 'installed_apps', []) else "#0984e3",
                                state="disabled" if appid in getattr(self, 'installed_apps', []) else "normal")
            btn.configure(command=lambda aid=appid, b=btn, br=bar: download_app(aid, b, br))
            btn.pack(side="right", padx=15, pady=15)
"""
code = code.replace(old_taskmgr, new_taskmgr)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 5 aplicado correctamente")
