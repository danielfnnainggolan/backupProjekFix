import os, sys
from PyQt5.QtWidgets import (
    QMainWindow, 
    QMessageBox, 
    QWidget, 
    QPushButton,
    QApplication
)
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent, pyqtSlot

import merek
import lokasi
import satuanjumlah
import satuanbarang
import katalog
import dashboard

class KatalogDashboard(QMainWindow):
    def __init__(self):
        super(KatalogDashboard, self).__init__()
        uic.loadUi("ui/katalog_dashboard.ui", self)

        self.setMouseTracking(True)
        
        # Initialize lists for widgets
        self._widgets = [[] for _ in range(7)]

        # Initialize pages
        self.katalog_page = katalog.KatalogFunction()
        self.merek_page = merek.MerekFunction()
        self.lokasiBarang = lokasi.LokasiFunction()
        self.satuanBarang = satuanbarang.SatuanBarangFunction()
        self.satuanJumlah = satuanjumlah.SatuanJumlahFunction()

        # Add pages to stacked widget
        self.stackedWidget.addWidget(self.katalog_page)
        self.stackedWidget.addWidget(self.merek_page)
        self.stackedWidget.addWidget(self.lokasiBarang)
        self.stackedWidget.addWidget(self.satuanBarang)
        self.stackedWidget.addWidget(self.satuanJumlah)
       
        # Connect buttons to their functions
        self.katalogBtn.clicked.connect(self.katalogStacked)
        self.katalogBtn1.clicked.connect(self.katalogStacked)
        self.merekBtn.clicked.connect(self.merekBarangStacked)
        self.merekBtn1.clicked.connect(self.merekBarangStacked)
        self.lokasiBtn.clicked.connect(self.lokasiBarangStacked)
        self.lokasiBtn1.clicked.connect(self.lokasiBarangStacked)
        self.satuanbarangBtn.clicked.connect(self.satuanbarangStacked)
        self.satuanbarangBtn1.clicked.connect(self.satuanbarangStacked)
        self.satuanjumlahBtn.clicked.connect(self.satuanjumlahStacked)
        self.satuanjumlahBtn1.clicked.connect(self.satuanjumlahStacked)
        self.exit.clicked.connect(self.exit_program)
        self.exit1.clicked.connect(self.exit_program)
        self.beranda.clicked.connect(self.home)
        self.beranda1.clicked.connect(self.home)
        
        # Add widgets for hover effect
        self.add_widget(1, self.katalogBtn)
        self.add_widget(1, self.katalogBtn1)
        self.add_widget(2, self.merekBtn)
        self.add_widget(2, self.merekBtn1)
        self.add_widget(3, self.lokasiBtn)
        self.add_widget(3, self.lokasiBtn1)
        self.add_widget(4, self.satuanbarangBtn)
        self.add_widget(4, self.satuanbarangBtn1)
        self.add_widget(5, self.satuanjumlahBtn)
        self.add_widget(5, self.satuanjumlahBtn1)
        self.add_widget(6, self.beranda)
        self.add_widget(6, self.beranda1)
        self.add_widget(7, self.exit)
        self.add_widget(7, self.exit1)

        self.merek_page.merek_deleted.connect(self.test)
        
    def add_widget(self, group, widget):
        """Add widget to a specific group for hover effects."""
        if not isinstance(widget, QWidget):
            raise TypeError(f"{widget} must be QWidget object")
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_Hover)
        self._widgets[group-1].append(widget)

    def eventFilter(self, obj, event):
        for i, widget_group in enumerate(self._widgets, 1):
            if obj in widget_group:
                if event.type() == QEvent.HoverEnter:
                    self.change_property(i, True)
                elif event.type() == QEvent.HoverLeave:
                    self.change_property(i, False)
        return super().eventFilter(obj, event)

    def change_property(self, group, hovered):
        for widget in self._widgets[group-1]:
            widget.setProperty("hovered", hovered)
            widget.style().polish(widget)

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

    @pyqtSlot(int)
    def test(self, value):
        self.katalog_page.loadDataWorker()

    def home(self):
        self.hide()
        self.window = QMainWindow()
        self.ui = dashboard.Dashboard()
        self.ui.show()

    def katalogStacked(self): 
        self.stackedWidget.setCurrentIndex(0)
       
    def merekBarangStacked(self):
        self.stackedWidget.setCurrentIndex(1)
        
    def lokasiBarangStacked(self):
        self.stackedWidget.setCurrentIndex(2)

    def satuanbarangStacked(self):
        self.stackedWidget.setCurrentIndex(3)
    
    def satuanjumlahStacked(self):
        self.stackedWidget.setCurrentIndex(4)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KatalogDashboard()
    window.show()
    sys.exit(app.exec_())