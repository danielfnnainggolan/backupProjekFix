from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow
)
from PyQt5.QtGui import QIcon
import opnameBarang, katalogDashboard,accountMaker, os, salesDashboard
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
            self.salesButton.setVisible(False)
        self.katalogButton.clicked.connect(self.katalogDashboard)
        self.keluarmasukBarang.clicked.connect(self.opnameDashboard)
        self.account.clicked.connect(self.account_maker)
        self.salesButton.clicked.connect(self.salesDashboard)
        

    def account_maker(self):
        
        self.window = QWidget()
        self.ui = accountMaker.accountMaker(parent=self)
        self.ui.show()
        self.hide()

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

    def salesDashboard(self):
        self.hide()
        self.window = QMainWindow()
        self.ui = salesDashboard.SalesDashboard()
        self.ui.show()