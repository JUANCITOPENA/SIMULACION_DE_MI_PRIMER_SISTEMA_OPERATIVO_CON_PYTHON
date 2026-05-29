# Plan Maestro: Mini Windows JPV v2.0 (Master Edition)

La v2.0 transformará el simulador en un entorno funcional que interactúa con el sistema de archivos real del usuario (dentro de un entorno controlado).

## 1. Nuevas Funcionalidades Reales
- **Explorador de Archivos:** Navegación por carpetas reales usando el módulo `os` de Python.
- **Gestión de Datos:** Crear, renombrar y eliminar archivos (.txt) y carpetas.
- **Bloc de Notas (Notepad JPV):** Editor de texto integrado para leer y guardar archivos reales.
- **Mi PC (Dashboard de Discos):** Visualización del espacio libre/total de los discos duros locales (usando `psutil`).
- **Personalización:** Cambio de fondo de pantalla y temas (Light/Dark).
- **Drag & Drop:** (Simulado) para mover iconos en el escritorio.

## 2. Requisitos Técnicos Adicionales
- `psutil`: Para obtener datos reales del hardware (discos, CPU, RAM).
- Carpeta Raíz: Se creará `C:\Users\User\Desktop\SISTEMAS OPERATIVOS\VIRTUAL_DRIVE` para que el SO opere ahí de forma segura.

## 3. Estructura de Archivos v2.0
- `main_v2.py`: Punto de entrada.
- `file_manager.py`: Lógica de operaciones de archivo.
- `system_apps.py`: Calculadora, Bloc de notas y Visor de Discos.
- `ui_components.py`: Clases para ventanas personalizadas y widgets.

## 4. Hoja de Ruta
1.  **Capa de Datos:** Implementar la lógica para listar y crear archivos en la carpeta virtual.
2.  **UI de Ventanas Pro:** Crear una clase de ventana con barra de título, botones de minimizar/maximizar y scroll.
3.  **App: Explorador:** Crear la vista de lista con iconos según la extensión del archivo.
4.  **App: Mi PC:** Integrar `psutil` para mostrar gráficas de los discos.
5.  **Refinamiento:** Iconos en alta resolución y efectos de transparencia.

---
**Arquitecto:** Gemini CLI Agent & Ing. Juancito Peña
**Estado:** En Desarrollo (v2.0 Pre-Alpha)

