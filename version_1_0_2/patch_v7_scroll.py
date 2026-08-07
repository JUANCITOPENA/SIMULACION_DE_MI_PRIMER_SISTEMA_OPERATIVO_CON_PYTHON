import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

old_start = """    def toggle_start_menu(self):
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        else:
            if self.context_menu: self.context_menu.destroy(); self.context_menu = None
            self.start_menu = ctk.CTkFrame(self.desktop, width=350, height=600, border_width=2, corner_radius=20)
            self.start_menu.place(x=10, y=self.desktop.winfo_height() - 610); self.start_menu.lift()
            ctk.CTkLabel(self.start_menu, text="SISTEMA JPV v4.2", font=("Segoe UI", 20, "bold")).pack(pady=20)
            app_f = ctk.CTkFrame(self.start_menu, fg_color="transparent"); app_f.pack(fill="both", expand=True, padx=10)
            apps = [("🗂️ Explorador", self.open_explorer), ("🌍 Navegador", self.open_browser), ("📽️ Video Player", self.open_video_player),
                    ("🖥️ Mi PC", self.open_my_pc), ("🗒️ Notepad", self.open_notepad), ("🧮 Calculadora", self.open_calc),
                    ("⚙️ Configuración", self.open_control_panel), ("📊 Task Manager", self.open_task_manager), ("💻 Terminal", self.open_terminal), ("🛒 App Store", self.open_app_store)]
            for n, c in apps:
                ctk.CTkButton(app_f, text=n, fg_color="transparent", anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            ctk.CTkLabel(self.start_menu, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=5)
            for tname in THEMES:
                ctk.CTkButton(self.start_menu, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=40, pady=1)
            ctk.CTkButton(self.start_menu, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=40, pady=10)"""

new_start = """    def toggle_start_menu(self):
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
                ctk.CTkButton(scroll_f, text=n, fg_color="transparent", anchor="w", height=40, command=lambda cmd=c: [cmd(), self.toggle_start_menu()]).pack(fill="x")
            
            ctk.CTkLabel(scroll_f, text="--- Personalización ---", font=("Segoe UI", 10)).pack(pady=10)
            
            for tname in THEMES:
                ctk.CTkButton(scroll_f, text=tname, height=28, fg_color=THEMES[tname][0], command=lambda t=tname: self.apply_theme(t)).pack(fill="x", padx=20, pady=2)
            
            ctk.CTkButton(scroll_f, text="🖼️ Siguiente Fondo", command=self.change_wallpaper, fg_color="#0984e3").pack(fill="x", padx=20, pady=15)"""

if old_start in code:
    code = code.replace(old_start, new_start)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("Patch 7 aplicado correctamente")
else:
    print("No se encontró el bloque a reemplazar")
