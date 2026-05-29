import customtkinter as ctk
import datetime
import tkinter as tk
from tkinter import messagebox

class MiniWindowsJPV(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la Ventana Principal (Escritorio)
        self.title("Mini Windows JPV v1.0 - Prototipo")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Fondo del Escritorio
        self.desktop_bg = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0)
        self.desktop_bg.pack(fill="both", expand=True)

        # Barra de Tareas (Taskbar)
        self.taskbar = ctk.CTkFrame(self, height=50, fg_color="#16213e", corner_radius=0)
        self.taskbar.pack(side="bottom", fill="x")

        # Botón Inicio
        self.start_button = ctk.CTkButton(self.taskbar, text="🪟 Inicio", width=80, 
                                          fg_color="#0f3460", hover_color="#533483",
                                          command=self.show_start_menu)
        self.start_button.pack(side="left", padx=10, pady=5)

        # Reloj en la Barra de Tareas
        self.clock_label = ctk.CTkLabel(self.taskbar, text="", font=("Segoe UI", 12, "bold"))
        self.clock_label.pack(side="right", padx=15)
        self.update_clock()

        # Área de Iconos del Escritorio
        self.create_desktop_icons()

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S\n%d/%m/%Y")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)

    def create_desktop_icons(self):
        # Mi PC
        self.create_icon("💻\nMi Equipo", 20, 20, "blue")
        # Documentos
        self.create_icon("📂\nDocumentos", 20, 120, "orange")
        # Papelera
        self.create_icon("🗑️\nPapelera", 20, 220, "gray")
        # Red
        self.create_icon("🌐\nNavegador", 20, 320, "green")

    def create_icon(self, text, x, y, color):
        icon_frame = ctk.CTkFrame(self.desktop_bg, fg_color="transparent", width=80, height=80)
        icon_frame.place(x=x, y=y)
        
        btn = ctk.CTkButton(icon_frame, text=text, width=70, height=70, 
                             fg_color="transparent", hover_color="#2c2c54",
                             font=("Segoe UI", 11), compound="top",
                             command=lambda t=text: self.open_app(t))
        btn.pack()

    def open_app(self, app_name):
        # Limpiar el nombre del app (quitar emoji y salto de línea)
        clean_name = app_name.split("\n")[-1]
        
        # Crear una "Ventana" simulada
        win = ctk.CTkToplevel(self)
        win.title(f"Sistema - {clean_name}")
        win.geometry("400x300")
        win.attributes("-topmost", True)
        
        label = ctk.CTkLabel(win, text=f"Accediendo a: {clean_name}...", font=("Segoe UI", 14))
        label.pack(pady=20)
        
        content = ctk.CTkTextbox(win, width=350, height=180)
        content.pack(pady=10)
        content.insert("0.0", f"--- Explorador de {clean_name} ---\n\nEstado: Operacional\nUbicación: C:\\Users\\Juancito\\{clean_name}\n\nNo hay archivos en esta carpeta (v1.0)")
        
        close_btn = ctk.CTkButton(win, text="Cerrar", command=win.destroy)
        close_btn.pack(pady=10)

    def show_start_menu(self):
        messagebox.showinfo("Menú Inicio", "Mini Windows JPV\nVersión 1.0.0\n\nDesarrollado por Ing. Juancito Peña\nSistema Estable y Ligero.")

if __name__ == "__main__":
    app = MiniWindowsJPV()
    app.mainloop()
