import os
import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                            QMessageBox, QComboBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from qt_material import apply_stylesheet

class WindowsDNSChanger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DNS Changer")
        self.setFixedSize(600, 500)
        
        self.font = QFont("Segoe UI", 10)
        self.font.setBold(True)
        
        self.init_ui()
        self.interfaces = self.get_network_interfaces()
        self.update_interface_combo()
        
        apply_stylesheet(self, theme='dark_amber.xml')


    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # عنوان
        title = QLabel("تغییر دهنده DNS ویندوز")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #FFD700; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # انتخاب اینترفیس
        interface_layout = QHBoxLayout()
        interface_layout.addWidget(QLabel("آداپتور شبکه:"))
        
        self.interface_combo = QComboBox()
        self.interface_combo.setFont(self.font)
        interface_layout.addWidget(self.interface_combo)
        
        main_layout.addLayout(interface_layout)

        # سرورهای DNS
        dns_label = QLabel("سرورهای DNS")
        dns_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        dns_label.setStyleSheet("color: #FFD700; margin-top: 5px; margin-bottom: 5px;")
        main_layout.addWidget(dns_label)

        # دکمه‌های DNS
        dns_buttons = QWidget()
        dns_layout = QVBoxLayout(dns_buttons)
        dns_layout.setSpacing(5)
        
        self.create_dns_button(dns_layout, "EA DNS", ['178.22.122.100', '185.51.200.2'])
        self.create_dns_button(dns_layout, "Steam DNS", ['78.157.42.101', '78.157.42.100'])
        self.create_dns_button(dns_layout, "Begzar DNS", ['185.55.226.26', '185.55.225.25'])
        self.create_dns_button(dns_layout, "Shecan", ['178.22.122.100', '185.51.200.2'])
        
        main_layout.addWidget(dns_buttons)

        # دکمه پاک کردن خودکار DNS
        reset_btn = QPushButton("پاک کردن خودکار DNS")
        reset_btn.setFont(self.font)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #FF5722;
                color: black;
                padding: 8px;
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #FF7043;
            }
        """)
        reset_btn.clicked.connect(self.reset_dns)
        main_layout.addWidget(reset_btn)

    def create_dns_button(self, layout, name, servers):
        btn = QPushButton(name)
        btn.setFont(self.font)
        btn.setStyleSheet("""
            QPushButton {
                text-align: center;
                padding: 8px;
                background: #616161;
                border-radius: 5px;
                color: #FFD700;
            }
            QPushButton:hover {
                background: #757575;
            }
        """)
        btn.clicked.connect(lambda: self.change_dns(servers))
        layout.addWidget(btn)

    def refresh_interfaces(self):
        self.interfaces = self.get_network_interfaces()
        self.update_interface_combo()

    def update_interface_combo(self):
        self.interface_combo.clear()
        for interface in self.interfaces:
            self.interface_combo.addItem(interface)

    def get_selected_interface(self):
        index = self.interface_combo.currentIndex()
        if 0 <= index < len(self.interfaces):
            return self.interfaces[index]
        return None

    def get_network_interfaces(self):
        try:
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                 capture_output=True, text=True, shell=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
            return [' '.join(line.split()[3:]) for line in result.stdout.split('\n')[3:] if line.strip()]
        except:
            return []

    def change_dns(self, dns_servers):
        interface = self.get_selected_interface()
        if not interface:
            return
            
        try:
            subprocess.run(['netsh', 'interface', 'ipv4', 'set', 'dnsservers', 
                          f'name="{interface}"', 'static', dns_servers[0], 'primary'], 
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if len(dns_servers) > 1:
                subprocess.run(['netsh', 'interface', 'ipv4', 'add', 'dnsservers', 
                              f'name="{interface}"', dns_servers[1], 'index=2'], 
                             shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            QMessageBox.information(self, "موفقیت", "DNS با موفقیت تغییر یافت")
        except:
            QMessageBox.critical(self, "خطا", "تغییر DNS ناموفق بود")

    def reset_dns(self):
        interface = self.get_selected_interface()
        if not interface:
            return
            
        try:
            subprocess.run(['netsh', 'interface', 'ipv4', 'set', 'dnsservers', 
                          f'name="{interface}"', 'dhcp'], 
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            subprocess.run(['ipconfig', '/flushdns'], 
                         shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            QMessageBox.information(self, "موفقیت", "DNS به حالت پیشفرض بازگردانده شد")
        except:
            QMessageBox.critical(self, "خطا", "بازگردانی DNS ناموفق بود")

if __name__ == "__main__":
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = WindowsDNSChanger()
    window.show()
    sys.exit(app.exec_())
