import os, sys, connection
import dashboard
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QDesktopWidget,
    QLineEdit,
    QWidget,
    QMessageBox,
)

# from file import Merek
from secret import MyApp

from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import (
    Qt, 
    QEvent,
)




class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi("ui/login.ui", self)
        self.setFixedWidth(800)
        self.setFixedHeight(687)
        self.loginButton.clicked.connect(self.loginfunction)
        self.password.returnPressed.connect(self.loginfunction)
        self.password.setEchoMode(QLineEdit.Password)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.center()
        self.password.installEventFilter(self)
        self.groupBox.setVisible(False)


    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        

    def loginfunction(self):
        mydb = connection.Connect()
        password = self.password.text()
        username = self.username.text().lower()
        error = connection.Error()
        try:
            mycursor = mydb.cursor()
            mycursor.execute("SELECT id,username, password, role_name FROM role_info WHERE username = %s",(str(username),))
            myresult = mycursor.fetchall()
            mycursor.close()
            mydb.close()
        except error as err:
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong")
            msgBox1.setIcon(QMessageBox.Warning)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowTitle("Data Kosong")
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            ret1 = msgBox1.exec()
        else:
            if myresult[0][2] == password:
                app = MyApp.instance()
                app.role_id = str(myresult[0][3])
                app.username = str(myresult[0][1])
                self.openWindow()
            else:
                msgBox1 = QMessageBox()
                msgBox1.setText("Password salah")
                msgBox1.setIcon(QMessageBox.Warning)
                msgBox1.setStandardButtons(QMessageBox.Ok)
                msgBox1.setWindowTitle("Gagal Masuk")
                msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
                ret1 = msgBox1.exec()
                self.password.clear()
        


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def openWindow(self):
        self.close()
        self.window = QWidget()
        self.ui = dashboard.Dashboard()
        self.ui.show()
    
    def eventFilter(self, source, event): #TODO: just another dream not realized
        if event.type() == QEvent.KeyPress:
            if event.modifiers() != Qt.ShiftModifier:
                if event.text().isupper():
                    self.groupBox.setVisible(True)
                elif event.key() == Qt.Key_CapsLock:
                    self.groupBox.setVisible(False)
 
            elif event.modifiers() == Qt.ShiftModifier:
                return False
            elif event.key() and not event.text().isupper():
                self.groupBox.setVisible(False)


        
            
        return super().eventFilter(source, event)








    
    # -------------------------------------------- end for buttons function

    

    

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def main():
    app = QApplication(sys.argv)
    mainWindow = Login()
    mainWindow.show()
    app.exec_()

if __name__ == '__main__':
    main()