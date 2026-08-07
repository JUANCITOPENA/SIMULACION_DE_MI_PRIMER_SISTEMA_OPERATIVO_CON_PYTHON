import os
import re

file_path = r"C:\Users\User\Desktop\SISTEMAS OPERATIVOS\version_1_0_2\main.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update InternalWindow class
new_internal_window = """class InternalWindow(ctk.CTkFrame):
    def __init__(self, master, app_id, title="Ventana", width=500, height=400, on_close=None, on_minimize=None, theme_colors=None, **kwargs):
        bg_col = theme_colors[2] if theme_colors else "#2c3e50"
        super().__init__(master, width=width, height=height, corner_radius=10, 
                         border_width=2, border_color="#34495e", fg_color=bg_col, **kwargs)
        
        self.app_id = app_id
        self.on_close = on_close
        self.on_minimize = on_minimize
        self.is_maximized = False
        self.old_geometry = {"x": 300, "y": 100, "w": width, "h": height}
        
        # Barra de Título
        self.title_bar = ctk.CTkFrame(self, height=35, fg_color="#34495e", corner_radius=10)
        self.title_bar.pack(fill="x", side="top", padx=2, pady=2)
        
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=("Segoe UI", 12, "bold"))
        self.title_label.pack(side="left", padx=10)
        
        # Botones de control
        self.close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25, 
                                        fg_color="#e81123", hover_color="#f1707a", command=self.close_window)
        self.close_btn.pack(side="right", padx=5)
        
        self.max_btn = ctk.CTkButton(self.title_bar, text="□", width=30, height=25, 
                                        fg_color="transparent", hover_color="#555555", command=self.toggle_maximize)
        self.max_btn.pack(side="right", padx=2)
        
        self.min_btn = ctk.CTkButton(self.title_bar, text="—", width=30, height=25, 
                                        fg_color="transparent", hover_color="#555555", command=self.minimize_window)
        self.min_btn.pack(side="right", padx=2)
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Resize grip
        self.grip = ctk.CTkFrame(self, width=15, height=15, fg_color="gray", corner_radius=0)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<B1-Motion>", self.do_resize)
        
        self.title_bar.bind("<Button-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.bind("<Button-1>", lambda e: self.lift())

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
        self.configure(width=new_w, height=new_h)
        self.place(width=new_w, height=new_h)

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
"""

# Replace InternalWindow
content = re.sub(r'class InternalWindow\(ctk\.CTkFrame\):.*?(?=\nclass MiniWindowsV4)', new_internal_window, content, flags=re.DOTALL)

# 2. Update __init__ in MiniWindowsV4 to add dynamic taskbar and bindings
init_repl = """
        # Taskbar
        self.taskbar = ctk.CTkFrame(self, height=50, fg_color=("#dfe6e9", "#2d3436"), corner_radius=0)
        self.taskbar.pack(side="bottom", fill="x")

        # Botones Taskbar
        self.start_btn = ctk.CTkButton(self.taskbar, text="🪟", width=50, height=40,
                                        fg_color=THEMES[self.current_theme][0], 
                                        command=self.toggle_start_menu)
        self.start_btn.pack(side="left", padx=10, pady=5)
        
        # Contenedor para apps abiertas en la barra de tareas
        self.apps_tb_frame = ctk.CTkFrame(self.taskbar, fg_color="transparent")
        self.apps_tb_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.vol_frame = ctk.CTkFrame(self.taskbar, fg_color="transparent")
        self.vol_frame.pack(side="right", padx=10)
        self.vol_label = ctk.CTkLabel(self.vol_frame, text="🔊", font=("Segoe UI", 14))
        self.vol_label.pack(side="left", padx=5)
        self.vol_slider = ctk.CTkSlider(self.vol_frame, from_=0, to=1, width=100, command=self.change_volume)
        self.vol_slider.set(1.0); self.vol_slider.pack(side="left")

        self.clock_btn = ctk.CTkButton(self.taskbar, text="", font=("Consolas", 12, "bold"),
                                        fg_color="transparent", width=150, command=self.open_calendar)
        self.clock_btn.pack(side="right", padx=5)
        
        # Eventos del Escritorio
        self.bg_label.bind("<Button-1>", self.on_desktop_click)
        self.bg_label.bind("<Button-3>", self.show_context_menu)
        
        self.context_menu = None
"""
content = re.sub(r'# Taskbar.*?self\.start_menu = None\n\s*self\.load_wallpaper\(\)', init_repl + "        self.start_menu = None\n        self.load_wallpaper()", content, flags=re.DOTALL)


# 3. Add taskbar button management and context menu methods
new_methods = """
    def on_desktop_click(self, event):
        if self.start_menu: self.start_menu.destroy(); self.start_menu = None
        if self.context_menu: self.context_menu.destroy(); self.context_menu = None

    def show_context_menu(self, event):
        self.on_desktop_click(None) # Ocultar otros menús
        self.context_menu = ctk.CTkFrame(self.desktop, width=150, corner_radius=5, border_width=1, border_color="gray")
        self.context_menu.place(x=event.x, y=event.y)
        
        opts = [
            ("🔄 Refrescar", lambda: [self.context_menu.destroy(), self.load_wallpaper()]),
            ("📁 Nueva Carpeta", lambda: [self.context_menu.destroy(), self.create_new_folder()]),
            ("📄 Nuevo Archivo", lambda: [self.context_menu.destroy(), self.create_new_file()]),
            ("⚙️ Propiedades", lambda: [self.context_menu.destroy(), self.open_control_panel()])
        ]
        
        for name, cmd in opts:
            ctk.CTkButton(self.context_menu, text=name, anchor="w", fg_color="transparent", 
                          hover_color="#555555", command=cmd).pack(fill="x", padx=2, pady=2)
                          
    def create_new_folder(self):
        name = simpledialog.askstring("Nueva Carpeta", "Nombre de la carpeta:")
        if name:
            os.makedirs(os.path.join(ROOT_DIR, name), exist_ok=True)
            messagebox.showinfo("Sistema", "Carpeta creada.")
            
    def create_new_file(self):
        name = simpledialog.askstring("Nuevo Archivo", "Nombre del archivo (ej. notas.txt):")
        if name:
            with open(os.path.join(ROOT_DIR, name), "w") as f: f.write("")
            messagebox.showinfo("Sistema", "Archivo creado.")

    def update_taskbar_buttons(self):
        for widget in self.apps_tb_frame.winfo_children():
            widget.destroy()
            
        for app_id, win in self.running_apps.items():
            btn = ctk.CTkButton(self.apps_tb_frame, text=win.title_label.cget("text"), width=120, height=35,
                                fg_color="transparent", border_width=1, border_color="gray",
                                hover_color="#555555", command=lambda aid=app_id: self.restore_app(aid))
            btn.pack(side="left", padx=5)

    def restore_app(self, app_id):
        if app_id in self.running_apps:
            win = self.running_apps[app_id]
            if not win.winfo_viewable():
                win.place(x=win.old_geometry["x"], y=win.old_geometry["y"], width=win.old_geometry["w"], height=win.old_geometry["h"])
            win.lift()

    def on_app_minimize(self, app_id):
        pass # La ventana ya hace place_forget() en InternalWindow
        
    def request_app(self, app_id, title, size):
        if app_id in self.running_apps:
            self.restore_app(app_id)
            return None
        win = InternalWindow(self.desktop, app_id, title, *map(int, size.split('x')), 
                             on_close=self.on_app_close, on_minimize=self.on_app_minimize, theme_colors=THEMES[self.current_theme])
        self.running_apps[app_id] = win
        win.place(x=200, y=100, width=int(size.split('x')[0]), height=int(size.split('x')[1]))
        self.update_taskbar_buttons()
        return win

    def on_app_close(self, app_id):
        if app_id in self.running_apps: 
            del self.running_apps[app_id]
            self.update_taskbar_buttons()
"""

# Replace request_app and on_app_close block, and insert new methods
content = re.sub(r'    def request_app\(self, app_id, title, size\):.*?(?=\n    # --- VIDEO PLAYER)', new_methods, content, flags=re.DOTALL)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Actualizado main.py")
