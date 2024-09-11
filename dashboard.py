from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow
)
from PyQt5.QtGui import QIcon
import opnameBarang, katalogDashboard,accountMaker, os
from secret import MyApp
from PyQt5 import uic

class Dashboard(QWidget):
    def __init__(self):
        super(Dashboard, self).__init__()
        uic.loadUi("ui/dashboard.ui", self)
        app = MyApp.instance()
        role = app.role_id
        username = app.username
        self.setWindowTitle("Selamat Datang %s" % username)
        self.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
        
        if role == "superadmin":  
            self.account.setVisible(True)
        elif role == "warehouse":  
            self.account.setVisible(False)        
        self.katalogButton.clicked.connect(self.katalogDashboard)
        self.keluarmasukBarang.clicked.connect(self.opnameDashboard)
        self.account.clicked.connect(self.account_maker)
        

    def account_maker(self):
        self.hide()
        self.window = QWidget()
        self.ui = accountMaker.accountMaker()
        self.ui.show()

    def katalogDashboard(self):
        self.hide()
        self.window = QMainWindow()
        self.ui = katalogDashboard.KatalogDashboard()
        self.ui.show()

    def opnameDashboard(self):
        self.hide()
        self.window = QMainWindow()
        self.ui = opnameBarang.opnameFunction()
        self.ui.show()