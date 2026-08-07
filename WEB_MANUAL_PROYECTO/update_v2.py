import os
import re

html_path = r"C:\Users\User\Desktop\SISTEMAS OPERATIVOS\WEB_MANUAL_PROYECTO\index.html"
v2_path = r"C:\Users\User\Desktop\SISTEMAS OPERATIVOS\version_1_0_2\main.py"

with open(v2_path, "r", encoding="utf-8") as f:
    v2_code = f.read()

# Make it HTML safe
v2_code = v2_code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

new_sections = f"""
        <hr class="my-5" style="border-top: 3px dashed #3498db;">

        <!-- PRESENTACIÓN V2.0 -->
        <section id="presentacion-v2">
            <h1 class="section-title text-center text-primary" style="font-size: 3rem;"><i class="fa-solid fa-rocket"></i> MINI WINDOWS V2.0 PRO</h1>
            
            <div class="card card-custom p-4 mb-4 shadow" style="background: linear-gradient(135deg, #0984e3, #6c5ce7); color: white; border-radius: 20px;">
                <h3 class="fw-bold"><i class="fa-solid fa-star text-warning"></i> La Evolución del Sistema</h3>
                <p class="lead mt-3">
                    La versión 2.0 no es solo una actualización, es un <strong>salto generacional</strong>. Hemos convertido una simple maqueta en un entorno persistente con características avanzadas propias de sistemas operativos modernos.
                </p>
                <div class="row mt-4">
                    <div class="col-md-6 mb-3">
                        <h5 class="text-warning"><i class="fa-solid fa-floppy-disk"></i> Persistencia de Datos (settings.json)</h5>
                        <p class="small">El sistema ahora recuerda tus fondos de pantalla, tu tema oscuro/claro y el volumen gracias a la escritura en disco de archivos JSON.</p>
                    </div>
                    <div class="col-md-6 mb-3">
                        <h5 class="text-warning"><i class="fa-solid fa-up-right-and-down-left-from-center"></i> Redimensionamiento y Maximización</h5>
                        <p class="small">Las ventanas ya no son estáticas. Implementamos algoritmos de <em>Resizing</em> con bordes activos y botones de maximización y minimización.</p>
                    </div>
                    <div class="col-md-6 mb-3">
                        <h5 class="text-warning"><i class="fa-brands fa-chrome"></i> Navegador Web Real (PyQt6 / Webview)</h5>
                        <p class="small">Reemplazamos el visor HTML básico por el motor de Chromium de PyQt6 o un Webview nativo, ejecutado en un proceso separado para no saturar la UI principal.</p>
                    </div>
                    <div class="col-md-6 mb-3">
                        <h5 class="text-warning"><i class="fa-solid fa-terminal"></i> Terminal, App Store y Administrador de Tareas</h5>
                        <p class="small">Nuevas aplicaciones internas: Un <strong>Task Manager</strong> que mata procesos colgados, una <strong>Terminal</strong> interactiva y una tienda de apps que simula descargas asíncronas.</p>
                    </div>
                    <div class="col-md-12">
                        <h5 class="text-warning"><i class="fa-solid fa-computer-mouse"></i> Menú Contextual (Clic Derecho)</h5>
                        <p class="small">Ahora puedes hacer clic derecho en el escritorio para crear carpetas, archivos, refrescar los íconos o cambiar propiedades en tiempo real.</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- ESTRUCTURA V2 -->
        <section id="estructura-v2">
            <h2 class="section-title"><i class="fa-solid fa-folder-tree"></i> 9. Estructura de Archivos (Versión 2.0)</h2>
            <div class="card card-custom p-4 mb-4 shadow-sm" style="background-color: #1e1e1e; color: #d4d4d4;">
                <pre style="background-color: transparent; border: none; color: inherit; font-family: 'Consolas', monospace; font-size: 15px; margin: 0;"><span style="color: #4daafc;">📂 SISTEMAS OPERATIVOS V2 /</span>
│
├── <span style="color: #f1c40f;"><i class="fa-brands fa-python"></i> main.py</span>                    <span style="color: #6a9955;"># El nuevo motor principal V2.0</span>
├── <span style="color: #f1c40f;"><i class="fa-brands fa-python"></i> browser_engine.py</span>          <span style="color: #6a9955;"># (Opcional) Motor web aislado basado en PyQt6</span>
│
├── <span style="color: #4daafc;">📂 assets /</span>                  <span style="color: #6a9955;"># Íconos para la barra de tareas e interfaz</span>
│   ├── <span style="color: #4daafc;">📂 wallpapers /</span>          <span style="color: #6a9955;"># Fondos HD (El sistema crea un default.png si está vacío)</span>
│   └── <span style="color: #ce9178;">start.png, explorer.png...</span> <span style="color: #6a9955;"># Iconos del escritorio y barra de tareas</span>
│
├── <span style="color: #4daafc;">📂 VIRTUAL_DRIVE /</span>           <span style="color: #6a9955;"># Directorio de sistema del usuario</span>
│   └── <span style="color: #ce9178;">settings.json</span>            <span style="color: #6a9955;"># [Auto] Guarda configuraciones de volumen, fondo y tema</span>
│
└── <span style="color: #4daafc;">📂 temp /</span>                    <span style="color: #6a9955;"># Extractor temporal de Audio (MoviePy)</span></pre>
            </div>
        </section>

        <!-- INSTALACIÓN V2 -->
        <section id="instalacion-v2">
            <h2 class="section-title"><i class="fa-solid fa-screwdriver-wrench"></i> 10. Instalación y Dependencias (V2.0)</h2>
            <p>La nueva versión requiere algunas librerías adicionales para soportar el navegador Chromium y las utilidades avanzadas.</p>
            
            <div class="code-container">
                <button class="copy-btn" onclick="copiarCodigo(this)"><i class="fa-regular fa-copy"></i> Copiar</button>
                <pre><code class="language-bash">python -m pip install customtkinter pillow psutil opencv-python numpy pygame-ce moviepy tkcalendar PyQt6 PyQt6-WebEngine pywebview</code></pre>
            </div>

            <h5 class="mt-4"><i class="fa-solid fa-plus text-success"></i> Nuevas Librerías Añadidas:</h5>
            <ul class="list-group shadow-sm mb-4">
                <li class="list-group-item"><strong><code>PyQt6</code> y <code>PyQt6-WebEngine</code></strong>: Frameworks pesados de C++ portados a Python. Contienen el motor real de Google Chrome (Chromium) para renderizar webs 100% modernas (YouTube, HTML5, etc.).</li>
                <li class="list-group-item"><strong><code>pywebview</code></strong>: Una alternativa ligera que utiliza el motor web nativo del sistema operativo (Edge WebView2 en Windows) sin necesidad de instalar PyQt6.</li>
            </ul>
        </section>

        <!-- CÓDIGO V2 -->
        <section id="codigo-v2">
            <h2 class="section-title"><i class="fa-solid fa-code"></i> 11. El Código Completo V2.0 (main.py)</h2>
            <p>Reemplaza todo tu código antiguo por este. Incluye todas las mejoras de UI, persistencia y multitarea.</p>
            
            <div class="code-container">
                <button class="copy-btn" onclick="copiarCodigo(this)"><i class="fa-regular fa-copy"></i> Copiar Código</button>
<pre><code class="language-python">{v2_code}</code></pre>
            </div>
        </section>

        <!-- COMPILACIÓN V2 -->
        <section id="compilacion-v2">
            <h2 class="section-title"><i class="fa-solid fa-box-open"></i> 12. Ejecución, Ejecutable e Instalador (V2.0)</h2>
            
            <div class="row">
                <div class="col-md-6 mb-4">
                    <div class="card card-custom p-4 h-100 shadow-sm border-start border-4 border-success">
                        <h4 class="fw-bold"><i class="fa-solid fa-play text-success"></i> 1. Ejecución en Pruebas</h4>
                        <p class="small text-muted">Ejecuta el sistema normalmente. Si deseas probar el navegador PyQt6 embebido, asegúrate de tener el archivo <code>browser_engine.py</code> en la misma carpeta.</p>
                        <div class="code-container mt-2">
                            <button class="copy-btn" onclick="copiarCodigo(this)"><i class="fa-regular fa-copy"></i></button>
                            <pre><code class="language-bash">python main.py</code></pre>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-4">
                    <div class="card card-custom p-4 h-100 shadow-sm border-start border-4 border-danger">
                        <h4 class="fw-bold"><i class="fa-solid fa-file-code text-danger"></i> 2. Empaquetado (.exe)</h4>
                        <p class="small text-muted">A diferencia de la V1, empaquetar PyQt6 requiere que el motor gráfico de Chrome se adjunte. Usa este comando avanzado de PyInstaller:</p>
                        <div class="code-container mt-2">
                            <button class="copy-btn" onclick="copiarCodigo(this)"><i class="fa-regular fa-copy"></i></button>
                            <pre><code class="language-bash">pyinstaller --noconsole --onefile --windowed --add-data "assets;assets" --name "MiniWindows_V2_Pro" main.py</code></pre>
                        </div>
                    </div>
                </div>
            </div>
        </section>
"""

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Insert before the closing container div
target = "    </div>\n\n    <!-- Footer -->"
if target in html_content:
    new_html = html_content.replace(target, new_sections + "\n" + target)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_html)
    print("Success")
else:
    print("Target not found")
