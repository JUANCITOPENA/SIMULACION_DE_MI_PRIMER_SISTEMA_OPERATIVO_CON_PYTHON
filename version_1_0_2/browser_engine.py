import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import *

class Browser(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("JPV Browser (Chromium V8)")
        self.setGeometry(100, 100, 1024, 768)
        
        # WebView
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        
        # Navigation bar
        navbar = QToolBar()
        navbar.setMovable(False)
        self.addToolBar(navbar)
        
        # Back Button
        back_btn = QAction('◀ Atrás', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)
        
        # Forward Button
        forward_btn = QAction('Adelante ▶', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)
        
        # Reload Button
        reload_btn = QAction('🔄 Recargar', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)
        
        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        
        # Update URL bar when URL changes
        self.browser.urlChanged.connect(self.update_url)

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            if "." in self.url_bar.text() and " " not in self.url_bar.text():
                q.setScheme("https")
            else:
                # Search google
                search_url = "https://www.google.com/search?q=" + self.url_bar.text().replace(" ", "+")
                q = QUrl(search_url)
        self.browser.setUrl(q)

    def update_url(self, q):
        self.url_bar.setText(q.toString())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("JPV Browser")
    
    start_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.google.com"
    window = Browser(start_url)
    window.show()
    sys.exit(app.exec())
