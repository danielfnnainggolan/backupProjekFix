from PyQt5.QtWidgets import QWidget, QSizePolicy, QTableWidgetItem, QDialog, QMessageBox, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtCore import Qt, pyqtSignal
from pytz import timezone
import connection, os



class SatuanJumlahFunction(QWidget):
    satuanJumlah_deleted = pyqtSignal(int)
    def __init__(self):
        super(SatuanJumlahFunction, self).__init__()
        uic.loadUi("ui/satuanjumlah.ui", self)
        self.satuanTable.setColumnHidden(0, True)
        
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        

        self.addButton.clicked.connect(self.addWindow)
        self.editButton.clicked.connect(self.editWindow)
        self.deleteButton.clicked.connect(self.deleteWindow)
        self.satuanTable.itemSelectionChanged.connect(self.singleClick)
        self.searchField.textChanged.connect(self.search)
        self.searchField.textEdited.connect(self.detect_edit)
        self.loadData()

        # self.searchField.textChanged.connect(self.search)
    
    def loadData(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id, satuan_jumlah FROM satuan_jumlah WHERE deleted_At IS NULL;")
        
        
        self.myresult = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        row = 0
        self.satuanTable.setRowCount(len(self.myresult))
        for satuan in self.myresult:
            self.satuanTable.setItem(row, 0, QTableWidgetItem(str(satuan[0])))
            self.satuanTable.setItem(row, 1, QTableWidgetItem(satuan[1]))
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
        msgBox.setText("Apakah Anda yakin untuk menghapus satuan ini ?")
        msgBox.setInformativeText("Nama Satuan Jumlah Barang : "+" "+self.data[1])
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
            mycursor.execute("UPDATE satuan_jumlah SET deleted_At = %s WHERE id = %s ;", (datetime.now(timezone('Asia/Jakarta')), self.data[0]))
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
        row = self.satuanTable.currentRow()
        for x in range(self.satuanTable.columnCount()):
            self.data.insert(x, self.satuanTable.item(row, x).text())
        return self.data

    def search(self):
        search = self.searchField.text().lower()
        myresult = [
            x
            for x in self.myresult
            if search in x[1].lower()
        ]

        self.satuanTable.clearContents()
        row = 0
        self.satuanTable.setRowCount(len(myresult))

        for satuan in myresult:
            self.satuanTable.setItem(row, 0, QTableWidgetItem(satuan[0]))
            self.satuanTable.setItem(row, 1, QTableWidgetItem(satuan[1]))
            row += 1
       
      
class Add(QDialog):
    def __init__(self, parent):
        super(Add, self).__init__()
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint )
        uic.loadUi("ui/addSingle.ui", self)
        self.parent = parent

        self.setWindowTitle("Tambah Satuan Jumlah Barang")
        self.editLine.setPlaceholderText("Cth: pcs")
        
        self.apply.clicked.connect(self.Add_Action)
        self.addButton.clicked.connect(self.Add_line_edit)
        self.minButton.clicked.connect(self.Remove_line_edit)
        self.remove = []
        
        self.line_edits = [self.editLine]
        self.index = self.verticalLayout.indexOf(self.horizontalLayout)

    def Remove_line_edit(self):
        if len(self.line_edits)>1:
            delete_this = len(self.line_edits)-1
            self.verticalLayout.removeWidget(self.line_edits[delete_this])
            self.setTabOrder(self.line_edits[len(self.line_edits)-2], self.addButton)
            self.line_edits[delete_this].deleteLater()
            
            self.adjustSize()

            
            self.line_edits.pop(delete_this)
            self.index = self.verticalLayout.indexOf(self.horizontalLayout)
        else:
            return ""


    def Add_line_edit(self):
        line_edit = QLineEdit()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        line_edit.setSizePolicy(sizePolicy)
        line_edit.setStyleSheet("border: 2px solid gray;padding: 0 1px;selection-background-color: darkgray;")
        line_edit.setFixedWidth(251)
        line_edit.setFixedHeight(31)
        line_edit.setPlaceholderText("Cth: pcs")
        self.verticalLayout.insertWidget(self.index,line_edit)
        
        

        
        self.line_edits.append(line_edit)
        self.setTabOrder(self.line_edits[len(self.line_edits)-2], self.line_edits[len(self.line_edits)-1])
        self.index+=1
        

    def get_text(self):
        arr = [[0 for i in range(1)] for j in range(len(self.line_edits))]
        # Retrieve text from all QLineEdit widgets
        for index, line_edit in enumerate(self.line_edits):
            if line_edit.text() == "":
                continue
            else :
                arr[index][0] = line_edit.text()    

        return tuple(arr)

    def Add_Action(self):
        text = self.get_text()

        mydb = connection.Connect()
        error = connection.Error()
        mycursor = mydb.cursor()
        try:
            query = "INSERT INTO satuan_jumlah (satuan_jumlah) VALUES (%s)"
            mycursor.executemany(query, text)    
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
        self.setWindowTitle("Ubah Satuan Jumlah Barang")
        self.editLine.setPlaceholderText("Cth: pcs")
        

    def loadData(self, edit_array): 
        self.editLine.setText(edit_array[1])

    def Edit_Action(self, edit_array):
        push = []
        push.insert(0, edit_array[0])
        push.insert(1, self.editLine.text())
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        query = "UPDATE satuan_jumlah SET satuan_jumlah = %s WHERE id = %s "

        try:
            mycursor.execute(query, (push[1], push[0]))    
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

    
    



        
        

       

       

