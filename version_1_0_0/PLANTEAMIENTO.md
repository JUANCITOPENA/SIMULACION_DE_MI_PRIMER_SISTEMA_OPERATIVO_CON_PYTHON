# Planteamiento del Sistema Operativo: Mini Windows JPV (v1.0)

Este documento detalla el diseño y la hoja de ruta para la creación de un simulador de sistema operativo ligero, intuitivo y funcional, diseñado por el Ing. Juancito Peña.

## 1. Concepto
**Mini Windows JPV** no es un kernel real (que requeriría años de desarrollo en C/Assembly), sino un **Simulador de Entorno de Escritorio (DE)** que corre sobre una capa lógica de Python. El objetivo es emular la experiencia de usuario de Windows con la máxima ligereza.

## 2. Requisitos de Instalación (Simulados)
- **Procesador:** Cualquier CPU moderno (1.0 GHz+).
- **RAM:** 512MB (Mínimo asignado al proceso).
- **Almacenamiento:** 50MB para archivos de sistema e iconos.
- **Dependencias:** Python 3.10+ y bibliotecas de UI moderna.

## 3. Stack Tecnológico (Herramientas)
- **Lenguaje:** Python (Versatilidad y rapidez).
- **Interfaz Gráfica (GUI):** `CustomTkinter` (Para un look moderno tipo Windows 11).
- **Manejo de Imágenes:** `Pillow` (PIL) para iconos y fondos.
- **IDE:** Visual Studio Code o Cursor.
- **Entorno de Ejecución:** Virtualizado mediante un script `main.py` autoejecutable.

## 4. Arquitectura de la v1.0
- **Capa 1 (Escritorio):** Fondo de pantalla dinámico, área de iconos.
- **Capa 2 (Taskbar):** Botón de inicio, Reloj en tiempo real, Indicador de estado.
- **Capa 3 (Sistema de Ventanas):** Clase base para ventanas arrastrables y cerrables.
- **Capa 4 (File System Simulator):** Diccionario de datos que simula carpetas y archivos.

## 5. Paso a Paso para el Desarrollo
1.  **Estructura:** Crear carpetas para `assets/` (iconos) y `core/` (lógica).
2.  **Escritorio:** Implementar la ventana principal en modo pantalla completa simulado.
3.  **Taskbar:** Diseñar la barra inferior con el reloj dinámico.
4.  **Sistema de Iconos:** Crear componentes clickeables que representen "Mi PC" o "Carpetas".
5.  **Gestor de Ventanas:** Programar la lógica para abrir/cerrar ventanas al hacer doble clic.
6.  **Pruebas (v1.0):** Ejecución y validación de la interfaz.

---
**Desarrollado por:** Gemini CLI Agent
**Para:** Ing. Juancito Peña
**Fecha:** Mayo 2026
