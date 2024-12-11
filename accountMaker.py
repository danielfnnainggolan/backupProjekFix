from PyQt5 import uic
from PyQt5.QtWidgets import ( 
    QWidget, 
    QTableWidgetItem, 
    QMessageBox, 
    QDialog,
    QLineEdit,
    QSizePolicy,
    QCompleter,QHBoxLayout)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from pytz import timezone
from datetime import datetime
from PyQt5.QtCore import Qt
import os, connection
from MyWidgets import CustomComboBox

class accountMaker(QWidget):
    def __init__(self, parent):
        super(accountMaker, self).__init__()
        uic.loadUi("ui/userAccount.ui", self)
        self.parentWindow = parent
        self.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
        self.loadData()
        self.addButton.clicked.connect(self.addWindow)
        self.editButton.clicked.connect(self.editWindow)
        self.deleteButton.clicked.connect(self.deleteWindow)
        self.accountTable.itemSelectionChanged.connect(self.singleClick)
        self.searchField.textChanged.connect(self.search)
        self.searchField.textEdited.connect(self.detect_edit)
    
    def closeEvent(self, event):
        if self.parentWindow:
            self.parentWindow.show()
        event.accept()
    
    def loadData(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id, id_role, username, role_name  FROM role_info;")
    
        self.myresult = mycursor.fetchall()
        mydb.close()
        row = 0
        self.accountTable.setRowCount(len(self.myresult))
        for account in self.myresult:
            self.accountTable.setItem(row, 0, QTableWidgetItem(str(account[0])))
            self.accountTable.setItem(row, 1, QTableWidgetItem(str(account[1])))
            self.accountTable.setItem(row, 2, QTableWidgetItem(account[2]))
            self.accountTable.setItem(row, 3, QTableWidgetItem(account[3]))
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
        msgBox.setText("Apakah Anda yakin untuk menghapus akun ini ?")
        msgBox.setInformativeText("Nama Akun : "+" "+self.data[1])
        msgBox.setWindowTitle("Konfirmasi Pilihan")
        msgBox.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        buttonY = msgBox.button(QMessageBox.Ok)
        buttonY.setText("Ya")
        
        buttonN = msgBox.button(QMessageBox.Cancel)
        buttonN.setText("Tidak")
        msgBox.setDefaultButton(buttonN)
        msgBox.exec()
        if msgBox.clickedButton() == buttonY:
            mydb = connection.Connect()
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE user SET deleted_At = %s WHERE id= %s ;", (datetime.now(timezone('Asia/Jakarta')), self.data[0]))
            mydb.commit()
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil dihapus")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            msgBox1.exec()
            self.loadData()

    def singleClick(self):  # enable edit button get item
        self.editButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.data = []
        row = self.accountTable.currentRow()
        for x in range(self.accountTable.columnCount()):
            self.data.insert(x, self.accountTable.item(row, x).text())
        return self.data

    def search(self):
        search = self.searchField.text().lower()
        myresult = [
            x
            for x in self.myresult
            if search in x[1].lower()
        ]

        self.accountTable.clearContents()
        row = 0
        self.accountTable.setRowCount(len(myresult))

        for account in myresult:
            self.accountTable.setItem(row, 0, QTableWidgetItem(str(account[0])))
            self.accountTable.setItem(row, 1, QTableWidgetItem(str(account[1])))
            self.accountTable.setItem(row, 2, QTableWidgetItem(account[2]))
            self.accountTable.setItem(row, 3, QTableWidgetItem(account[3]))
            row += 1

class Add(QDialog):
    def __init__(self, parent):
        super(Add, self).__init__()
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/addAccount.ui", self)
        self.parent = parent
        self.setWindowTitle("Tambah Akun")
        self.editLine.setPlaceholderText("Cth: Anto")
        self.apply.clicked.connect(self.Add_Action)
        
        self.addButton.clicked.connect(self.Add_line_edit)
        self.minButton.clicked.connect(self.Remove_line_edit)
        self.remove = []
        
        self.line_edits = [self.editLine]
        self.comboBox = [self.role]
        self.index = self.verticalLayout.indexOf(self.horizontalLayout_2)

        model = QStandardItemModel()

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT id, role_name FROM role_id where deleted_At is NULL")
        self.myresult = mycursor.fetchall()        
        mydb.close()
        

        for role in self.myresult:
            self.role.addItem(role[1], role[0])
    

        for i,word in enumerate(self.myresult):
            item = QStandardItem(word[1])
            model.setItem(i, 0, item)
            

        completer = QCompleter(self) 
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        
        self.role.setCompleter(completer)
        self.role.setSourceModel(model)
        self.role.lineEdit().setPlaceholderText("Pilih User Role")

    def Remove_line_edit(self):
        if len(self.line_edits)>1:
            #delete line_edit
            delete_this = len(self.line_edits)-1
            self.verticalLayout.removeWidget(self.line_edits[delete_this])
            self.line_edits[delete_this].deleteLater()
            self.line_edits.pop(delete_this)

            #delete_qcombobox
            delete_comboBox = len(self.comboBox)-1
            self.verticalLayout.removeWidget(self.comboBox[delete_comboBox])
            self.comboBox[delete_comboBox].deleteLater()
            self.comboBox.pop(delete_comboBox)

            #adjust tab order, delete horizontal layout and adjust
            self.setTabOrder(self.comboBox[len(self.comboBox)-2], self.addButton)
            self.verticalLayout.removeItem(self.verticalLayout.itemAt(self.verticalLayout.count() - 3))
            self.index = self.verticalLayout.indexOf(self.horizontalLayout_2)
           

        else:
            return ""
        self.adjustSize()


    def Add_line_edit(self):
        line_edit = QLineEdit()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line_edit.setSizePolicy(sizePolicy)
        line_edit.setStyleSheet("border: 2px solid gray;padding: 0 1px;selection-background-color: darkgray;")
        line_edit.setFixedHeight(31)
        line_edit.setPlaceholderText("Cth: Anto")
        

        #Custom Combo Box
        combobox = CustomComboBox()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        combobox.setSizePolicy(sizePolicy)
        combobox.setStyleSheet("QComboBox {border: 2px solid gray;border-radius:6px;border-bottom-left-radius:0px;"
                                "border-top-left-radius:0px;padding: 0 5px;selection-background-color: darkgray;border-left:0px}"
                                "QComboBox::drop-down {subcontrol-origin: padding;subcontrol-position: top right;width: 15px;"
                                "border-left-width: 1px;border-left-color: gray;border-left-style: solid;"
                                "border-top-right-radius: 6px;border-bottom-right-radius: 6px;}"
                                "QComboBox::down-arrow {image: url(:/newPrefix/drop-down-arrow.png);width: 13px;height: 13px;}"
                                "QComboBox::down-arrow:on {top: 1px;left: 1px;}"
                                "QComboBox QAbstractItemView {border: 3px solid darkgray;selection-background-color: gray;}")
        combobox.setFixedHeight(31)
        combobox.lineEdit().setPlaceholderText("Pilih User Role")



        model = QStandardItemModel()
        for role in self.myresult:
            combobox.addItem(role[1], role[0])
    

        for i,word in enumerate(self.myresult):
            item = QStandardItem(word[1])
            model.setItem(i, 0, item)
            

        completer = QCompleter(self) 
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        
        combobox.setCompleter(completer)
        combobox.setSourceModel(model)


        #append to array
        self.line_edits.append(line_edit)
        self.comboBox.append(combobox)

        #make new layout for line_edit and comboBox
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(line_edit)
        layout.addWidget(combobox)
    

        self.verticalLayout.insertLayout(self.index, layout)

        self.setTabOrder(self.line_edits[len(self.line_edits)-1], self.comboBox[len(self.comboBox)-1])
        self.index+=1
        

    def get_text(self):
        counter = 0
        arr = [[0 for i in range(3)] for j in range(len(self.line_edits))]
        # Retrieve text from all QLineEdit widgets
        for index, line_edit in enumerate(self.line_edits):
            if line_edit.text() == "":
                continue
            if self.comboBox[index].currentData() is None:
                continue
            else :
                #since comboBox quantity = line edit quantity its okay. Also create default password
                arr[index][0] = line_edit.text().lower()
                arr[index][1] = self.comboBox[index].currentData()          
                arr[index][2] = line_edit.text().lower()+"123"   #need to encrypt password, soon but not now  
                counter+=1
        if counter == 0:
            return "error"
        return tuple(arr)

    def Add_Action(self):
        text = self.get_text()
        mydb = connection.Connect()
        error = connection.Error()
        mycursor = mydb.cursor()
        try:
            query = "INSERT INTO user (username, role_id, password ) VALUES (%s, %s, %s)"
            mycursor.executemany(query, text)    
            mydb.commit()
            mydb.close()
        except error as err: 
            print("Database Update Failed !: {}".format(err))
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong")
            msgBox1.setIcon(QMessageBox.Warning)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowTitle("Data Kosong")
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.exec()
        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil ditambah")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            msgBox1.exec()
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
            mydb.close()
        except: 
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong")
            msgBox1.setIcon(QMessageBox.Warning)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowTitle("Data Kosong")
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.exec()
        else:
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil diubah")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            msgBox1.exec()
            self.parent.loadData()
            self.close()
       
