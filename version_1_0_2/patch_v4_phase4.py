import os

file_path = "main.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Fix 1: InternalWindow Propagate and Themes
old_init = """class InternalWindow(ctk.CTkFrame):
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, on_minimize=None, theme_colors=None, **kwargs):
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        super().__init__(master, width=width, height=height, corner_radius=10, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        self.app_id = app_id
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.is_maximized = False
        self.old_geometry = {"x": 300, "y": 100, "w": width, "h": height}
        
        self.title_bar = ctk.CTkFrame(self, height=35, fg_color="#34495e", corner_radius=10)
        self.title_bar.pack(fill="x", side="top", padx=2, pady=2)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=10)
        
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, fg_color="#e81123", hover_color="#f1707a", command=self.close_window)
        self.close_btn.pack(side="right", padx=2)
        
        self.max_btn = ctk.CTkButton(self.title_bar, text="□", width=30, height=25, fg_color="transparent", hover_color="#555555", command=self.toggle_maximize)
        self.max_btn.pack(side="right", padx=2)
        
        self.min_btn = ctk.CTkButton(self.title_bar, text="_", width=30, height=25, fg_color="transparent", hover_color="#555555", command=self.minimize_window)
        self.min_btn.pack(side="right", padx=2)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=5, pady=5)"""

new_init = """class InternalWindow(ctk.CTkFrame):
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
        self.content.pack_propagate(False)"""

code = code.replace(old_init, new_init)

# Fix 2: Add Wallpaper selector in context menu
old_context = """        opts = [
            ("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.load_wallpaper()]),
            ("📁 Nueva Carpeta", lambda: [self.context_menu.destroy(), self.create_new_folder()]),
            ("📄 Nuevo Archivo", lambda: [self.context_menu.destroy(), self.create_new_file()]),
            ("⚙️ Propiedades", lambda: [self.context_menu.destroy(), self.open_control_panel()])
        ]"""
new_context = """        opts = [
            ("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.load_wallpaper()]),
            ("📁 Nueva Carpeta", lambda: [self.context_menu.destroy(), self.create_new_folder()]),
            ("📄 Nuevo Archivo", lambda: [self.context_menu.destroy(), self.create_new_file()]),
            ("🖼️ Cambiar Fondo", lambda: [self.context_menu.destroy(), self.open_wallpaper_selector()]),
            ("⚙️ Propiedades", lambda: [self.context_menu.destroy(), self.open_control_panel()])
        ]"""
code = code.replace(old_context, new_context)

# Fix 3: Add open_wallpaper_selector function
new_wall_selector = """
    def open_wallpaper_selector(self):
        win = self.request_app("wallpapers", "Fondos de Pantalla", "500x400")
        if not win: return
        scroll = ctk.CTkScrollableFrame(win.content)
        scroll.pack(fill="both", expand=True)
        
        for idx, w in enumerate(self.wallpapers):
            ctk.CTkButton(scroll, text=f"🖼️ {w}", anchor="w", fg_color="transparent", 
                          command=lambda i=idx: [setattr(self, 'current_wallpaper_idx', i), self.load_wallpaper()]).pack(fill="x", pady=2)
"""
code = code.replace('    def open_control_panel(self):', new_wall_selector + '    def open_control_panel(self):')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 4 aplicado correctamente")
