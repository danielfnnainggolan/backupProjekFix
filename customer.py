from PyQt5.QtWidgets import QWidget, QLineEdit, QSizePolicy, QTableWidgetItem, QDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtCore import Qt
from pytz import timezone
import connection, os




class CustomerFunction(QWidget):
    
    def __init__(self):
        super(CustomerFunction, self).__init__()
        uic.loadUi("ui/customerList.ui", self)
        self.customerTable.setColumnHidden(0, True)
        self.loadData()
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)


        self.addButton.clicked.connect(self.addWindow)
        self.editButton.clicked.connect(self.editWindow)
        self.deleteButton.clicked.connect(self.deleteWindow)
        self.customerTable.itemSelectionChanged.connect(self.singleClick)
        self.searchField.textChanged.connect(self.search)
        self.searchField.textEdited.connect(self.detect_edit)
     
      
    def loadData(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id, nama, alamat, nomor_hp, email FROM customer WHERE deleted_At IS NULL;")
        
        self.myresult = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        row = 0
        self.customerTable.setRowCount(len(self.myresult))
        for customer in self.myresult:
            self.customerTable.setItem(row, 0, QTableWidgetItem(str(customer[0])))
            self.customerTable.setItem(row, 1, QTableWidgetItem(str(customer[1])))
            self.customerTable.setItem(row, 3, QTableWidgetItem(str(customer[2])))
            self.customerTable.setItem(row, 3, QTableWidgetItem(str(customer[3])))
            self.customerTable.setItem(row, 4, QTableWidgetItem(str(customer[4])))
            row += 1

    def detect_edit(self):
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
    
    def addWindow(self):
        self.add_child = Add(parent=self)
        self.add_child.show()

    def editWindow(self):
        self.edit_child = Edit(parent=self)
        self.edit_child.show()
    
    def deleteWindow(self):
        self.singleClick()
        msgBox = QMessageBox()
        msgBox.setText("Apakah Anda yakin untuk menghapus pelanggan ini ?")
        msgBox.setInformativeText("Nama Pelanggan : "+" "+self.data[1])
        msgBox.setWindowTitle("Konfirmasi Pilihan")
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
            mydb = connection.Connect()
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE customer SET deleted_At = %s WHERE id= %s ;", (datetime.now(timezone('Asia/Jakarta')), self.data[0]))
            mydb.commit()
            mycursor.close()
            mydb.close()
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil dihapus")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            ret1 = msgBox1.exec()
            self.loadData()

    def singleClick(self):  # enable edit button get item
        self.editButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.data = []
        row = self.customerTable.currentRow()
        for x in range(self.customerTable.columnCount()):
            self.data.insert(x, self.customerTable.item(row, x).text())
        return self.data

    def search(self):
        search = self.searchField.text().lower()
        myresult = [
            x
            for x in self.myresult
            if search in x[1].lower()
        ]

        self.customerTable.clearContents()
        row = 0
        self.customerTable.setRowCount(len(myresult))

        for customer in myresult:
            self.customerTable.setItem(row, 0, QTableWidgetItem(str(customer[0])))
            self.customerTable.setItem(row, 1, QTableWidgetItem(str(customer[1])))
            self.customerTable.setItem(row, 3, QTableWidgetItem(str(customer[2])))
            self.customerTable.setItem(row, 3, QTableWidgetItem(str(customer[3])))
            self.customerTable.setItem(row, 4, QTableWidgetItem(str(customer[4])))
            row += 1
       
      
class Add(QDialog):
    def __init__(self, parent):
        super(Add, self).__init__()
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/addCustomer.ui", self)
        self.parent = parent
        self.setWindowTitle("Tambah Data Pelanggan")
        self.editLine.setPlaceholderText("Cth: PT. Karya Graha Laboratory")
        self.apply.clicked.connect(self.Add_Action)
        

    def Add_Action(self):
        push = []
        push.insert(0, self.nama_pelanggan.text())
        push.insert(1, self.alamat_pelanggan.text())
        push.insert(2, self.nomor_hp.text())
        push.insert(3, self.email.text())

        mydb = connection.Connect()
        error = connection.Error()
        mycursor = mydb.cursor()
        try:
            query = "INSERT INTO customer (nama, alamat, nomor_hp, email, created_At) VALUES (%s, %s, %s, %s,%s)"
            mycursor.executemany(query, (push[0], push[1], push[2], push[3], datetime.now(timezone('Asia/Jakarta'))))    
            mydb.commit()
            mycursor.close()
            mydb.close()
        except error as err: 
            print("Database Update Failed !: {}".format(err))
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong")
            msgBox1.setIcon(QMessageBox.Warning)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowTitle("Data Kosong")
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            ret1 = msgBox1.exec()
        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil ditambah")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            ret1 = msgBox1.exec()
            self.parent.loadData()
            self.close()

class Edit(QDialog):
    def __init__(self, parent):
        super(Edit, self).__init__()
        self.setFixedSize(275, 31)
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/editSingle.ui", self)
        self.parent = parent
        edit_array = self.parent.singleClick()
        self.apply.clicked.connect(lambda:self.Edit_Action(edit_array))
        self.loadData(edit_array)
        self.setWindowTitle("Ubah Rak Barang")
        self.editLine.setPlaceholderText("Cth: Rak 1A")


    def loadData(self, edit_array): 
        self.editLine.setText(edit_array[1])

    def Edit_Action(self, edit_array):
        push = []
        push.insert(0, edit_array[0])
        push.insert(1, self.editLine.text())
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        query = "UPDATE lokasi SET lokasi = %s WHERE id = %s "

        try:
            mycursor.execute(query, (push[1].upper(), push[0]))    
            mydb.commit()
            mycursor.close()
            mydb.close()
        except: 
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong")
            msgBox1.setIcon(QMessageBox.Warning)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowTitle("Data Kosong")
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            ret1 = msgBox1.exec()
        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil diubah")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            ret1 = msgBox1.exec()
            self.parent.loadData()
            self.close()

    
    



        
        

       

       

