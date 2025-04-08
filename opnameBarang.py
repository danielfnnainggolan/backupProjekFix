from PyQt5.QtWidgets import (
    QMainWindow, 
    QMessageBox, 
    QWidget)
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtCore import Qt, QEvent, pyqtSlot
import os, stok , laporanstok, dashboard


class opnameFunction(QMainWindow):
    def __init__(self):
        super(opnameFunction, self).__init__()
        uic.loadUi("ui/opname_dashboard.ui", self)
        # self.ham_menu.clicked.connect(self.hamburgerfunction)

        self.setMouseTracking(True)
        self._widgets = []
        self._widgets1 = []
        self._widgets2 = []
        self._widgets3 = []





        self.stok_page = stok.StokFunction()
        self.laporanstok_page = laporanstok.LaporanStokFunction()
    
        


        self.stackedWidget.addWidget(self.stok_page)
        self.stackedWidget.addWidget(self.laporanstok_page)
       
       

        self.stokBtn.clicked.connect(self.stokBarangStacked)
        self.stokBtn1.clicked.connect(self.stokBarangStacked)

        self.reportBtn.clicked.connect(self.laporanStokStacked)
        self.reportBtn1.clicked.connect(self.laporanStokStacked)

        self.exit.clicked.connect(self.exit_program)
        self.exit1.clicked.connect(self.exit_program)

        self.beranda.clicked.connect(self.home)
        self.beranda1.clicked.connect(self.home)




    #--------------------------------------ADD WIDGET

        self.add_widget(self.stokBtn)
        self.add_widget(self.stokBtn1)

        
        self.add_widget1(self.reportBtn)
        self.add_widget1(self.reportBtn1)

        self.add_widget2(self.beranda)
        self.add_widget2(self.beranda1)

        self.add_widget3(self.exit)
        self.add_widget3(self.exit1)

        self.stok_page.stock_change.connect(self.test)

       

        

    #------------------------------------------------start multiple hovers
    
    @property
    def widgets(self):
        return self._widgets

    @property
    def widgets1(self):
        return self._widgets1

    @property
    def widgets2(self):
        return self._widgets2

    @property
    def widgets3(self):
        return self._widgets3

    
    def add_widget(self, widget):
        if not isinstance(widget, QWidget):
            raise TypeError(f"{widget} must be QWidget object")
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_Hover)
        self.widgets.append(widget)


    def add_widget1(self, widget):
        if not isinstance(widget, QWidget):
            raise TypeError(f"{widget} must be QWidget object")
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_Hover)
        self.widgets1.append(widget)

    def add_widget2(self, widget):
        if not isinstance(widget, QWidget):
            raise TypeError(f"{widget} must be QWidget object")
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_Hover)
        self.widgets2.append(widget)

    def add_widget3(self, widget):
        if not isinstance(widget, QWidget):
            raise TypeError(f"{widget} must be QWidget object")
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_Hover)
        self.widgets3.append(widget)
    

    def eventFilter(self, obj, event):
        if obj in self.widgets:
            if event.type() == QEvent.HoverEnter:
                self.change_property(True)
            elif event.type() == QEvent.HoverLeave:
                self.change_property(False)

        elif obj in self.widgets1:
            if event.type() == QEvent.HoverEnter:
                self.change_property1(True)
            elif event.type() == QEvent.HoverLeave:
                self.change_property1(False)

        elif obj in self.widgets2:
            if event.type() == QEvent.HoverEnter:
                self.change_property2(True)
            elif event.type() == QEvent.HoverLeave:
                self.change_property2(False)

        elif obj in self.widgets3:
            if event.type() == QEvent.HoverEnter:
                self.change_property3(True)
            elif event.type() == QEvent.HoverLeave:
                self.change_property3(False)

        return super().eventFilter(obj, event)

    def change_property(self, hovered):
        for widget in self.widgets:
            widget.setProperty("hovered", hovered)
            widget.style().polish(widget)

    def change_property1(self, hovered):
        for widget in self.widgets1:
            widget.setProperty("hovered", hovered)
            widget.style().polish(widget)
    
    def change_property2(self, hovered):
        for widget in self.widgets2:
            widget.setProperty("hovered", hovered)
            widget.style().polish(widget)
        
    def change_property3(self, hovered):
        for widget in self.widgets3:
            widget.setProperty("hovered", hovered)
            widget.style().polish(widget)
    

    #-------------------------------------------- end for multiple hovers

    #-----------------------------------------------start buttons function

    @pyqtSlot(int) #INI BUAT SINKRON DATA
    def test(self, value):
        self.laporanstok_page.loadData()

    def exit_program(self):
        msgBox = QMessageBox()
        msgBox.setText("Apakah Anda yakin untuk keluar dari program ini ?")
        msgBox.setWindowTitle("Keluar Program")
        msgBox.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        buttonY = msgBox.button(QMessageBox.Ok)
        buttonY.setText("Ya")
        
        buttonN = msgBox.button(QMessageBox.Cancel)
        buttonN.setText("Tidak")

        msgBox.setDefaultButton(buttonN)
        ret = msgBox.exec()
        if msgBox.clickedButton() == buttonY:
            self.close()

    def home(self):
        self.hide()
        self.window = QMainWindow()
        self.ui = dashboard.Dashboard()
        self.ui.show()


    #don't forget to load Data

    def stokBarangStacked(self):
        self.stackedWidget.setCurrentIndex(0)
        stok.StokFunction().loadData()

    def laporanStokStacked(self): 
        self.stackedWidget.setCurrentIndex(1)
        laporanstok.LaporanStokFunction().loadData() 
        
    
       