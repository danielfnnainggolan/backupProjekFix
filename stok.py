from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QWidget, QMessageBox,QCompleter, QCheckBox
from PyQt5.QtGui import QIcon,QStandardItemModel, QStandardItem
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
import connection, os
from secret import MyApp
from pytz import timezone
from WorkerOpname import WorkerThread, WorkerSQL




class StokFunction(QWidget):
    stock_change = pyqtSignal(int)
    
    def __init__(self):
        super(StokFunction, self).__init__()
        uic.loadUi("ui/stok.ui", self)
        self.total_page = None
        self.total_query = None
        self.workerSearch = None
        self.worker = None
        self.workerSQL = None
        self.current_page = 1
        self.limit_count = 25
        self.loadSQLWorker()

        self.stokTable.setColumnHidden(0, True)
        self.stokTable.setColumnHidden(1, True)
        self.stokTable.setColumnHidden(2, True)
        self.stokTable.setColumnHidden(3, True)
        
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)

        
        self.addButton.clicked.connect(self.addWindow)
        self.barangkeluar.clicked.connect(self.removeWindow)
        self.editButton.clicked.connect(self.editWindow)
        self.deleteButton.clicked.connect(self.deleteWindow)
        self.stokTable.itemSelectionChanged.connect(self.singleClick)
        self.searchField.textChanged.connect(self.search)
        self.searchField.textEdited.connect(self.detect_edit)
        self.loadDataWorker()
        # self.searchField.textChanged.connect(self.search)

        #pagination button initialize start
        self.buttons = [self.button1, self.button2, self.button3, self.button4]
        self.start.clicked.connect(self.pageStart)
        self.next.clicked.connect(self.pageNext)
        self.previous.clicked.connect(self.pagePrev)
        self.end.clicked.connect(self.pageEnd)
        for i, button in enumerate(self.buttons):
            button.clicked.connect(lambda _, b=button: self.pageClicked(int(b.text()), self.limit_count))
            if int(button.text()) == self.current_page:
                button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#ACACAC;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)

        #pagination button initialize end


    #Worker Function Start

    def loadDataWorker(self):
        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.stop()

        self.worker = WorkerThread(0,25)
        self.worker.result.connect(self.handle_result)
        self.worker.finished.connect(lambda :self.cleanup_worker(self.worker))
        self.worker.start()
    
    def handle_result(self, result):
        self.populateData(result)

    def loadSQLWorker(self):
        if self.workerSQL is not None:
            if self.workerSQL.isRunning():
                self.workerSQL.stop()

        self.workerSQL = WorkerSQL()
        self.workerSQL.data_emitted.connect(self.handle_sql_result)
        self.workerSQL.finished.connect(lambda : self.cleanup_worker(self.workerSQL))
        self.workerSQL.start()

    def handle_sql_result(self, total_query, total_page):
        self.total_query = total_query
        self.total_page = total_page
        self.jumlah_halaman.setText("Halaman %s dari %s halaman" %(self.current_page, total_page))

    def cleanup_worker(self, worker_name):
        if worker_name == self.worker:
            self.worker = None
        elif worker_name == self.workerSQL:
            self.workerSQL = None
        elif worker_name == self.workerSearch:
            self.workerSearch = None
        elif worker_name == self.workerExport:
            self.workerExport == None

    #Worker Function END


    def populateData(self, value):
        row = 0
        self.stokTable.setRowCount(len(value))
        for stok in value:
            self.stokTable.setItem(row, 0, QTableWidgetItem(str(stok[0])))
            self.stokTable.setItem(row, 1, QTableWidgetItem(str(stok[1])))
            self.stokTable.setItem(row, 2, QTableWidgetItem(str(stok[2])))
            self.stokTable.setItem(row, 3, QTableWidgetItem(stok[3]))
            self.stokTable.setItem(row, 4, QTableWidgetItem(stok[4]))
            self.stokTable.setItem(row, 5, QTableWidgetItem(stok[5]))
            self.stokTable.setItem(row, 6, QTableWidgetItem(stok[6]))
            self.stokTable.setItem(row, 7, QTableWidgetItem(stok[7]))
            self.stokTable.setItem(row, 8, QTableWidgetItem(str(stok[8])))
            self.stokTable.setItem(row, 9, QTableWidgetItem(str(stok[9])))
            row += 1


        
       

    def detect_edit(self):
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
    
    def addWindow(self):
        self.add_child = Add(parent=self)
        self.add_child.show()

    def removeWindow(self):
        self.add_child = Remove(parent=self)
        self.add_child.show()

    def editWindow(self):
        self.edit_child = Edit(parent=self)
        self.edit_child.show()
    
    def deleteWindow(self):
        self.singleClick()
        msgBox = QMessageBox()
        msgBox.setText("Apakah Anda yakin untuk menghapus stok ini ?")
        msgBox.setInformativeText("Nama Barang : "+" "+self.data[5])
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
            mycursor.execute("UPDATE stok SET deleted_At = %s WHERE id = %s ;", (datetime.now(), self.data[0]))
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
            self.stock_change.emit(42)

    def singleClick(self):  # enable edit button get item
        self.editButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.data = []
        row = self.stokTable.currentRow()
        for x in range(self.stokTable.columnCount()):
            self.data.insert(x, self.stokTable.item(row, x).text())
        return self.data

    def search(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select * FROM daftar_stok")
        
        self.search = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        search = self.searchField.text().lower()

        myresult = [
            x
            for x in self.search
            if search in x[4].lower()
            or search in x[5].lower()
            or search in x[6].lower()
            or search in x[7].lower()
            or search in x[8].lower()
            or search in x[9].lower()
        ]
        
        self.stokTable.clearContents()
        self.populateData(myresult)

    def pageClicked(self, page_number, limit):
        self.current_page = page_number
        page_number-=1
        self.worker = WorkerThread(page_number, limit)
        self.worker.start()
        self.worker.result.connect(self.handle_result)
        self.jumlah_halaman.setText("Halaman %s dari %s halaman" %(self.current_page, self.total_page))
        for i, button in enumerate(self.buttons):
            if int(button.text()) == self.current_page:
                    button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#ACACAC;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)
            else:
                button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#4E4E4E;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)

    def pageStart(self):
        self.loadSQLWorker()
        self.current_page = 1
        self.worker = WorkerThread(0, 25)
        self.worker.start()
        self.worker.result.connect(self.handle_result)
        for i, button in enumerate(self.buttons, start=1):
            button.setText(str(i))
            if int(button.text()) == self.current_page:
                    button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#ACACAC;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)
            else:
                button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#4E4E4E;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)

    

    def pageNext(self):
        
        limit = self.total_page
        if int(self.button4.text()) < limit:
            start_page = int(self.button1.text())
            for i, button in enumerate(self.buttons, start=start_page):
                button.setText(str(i+1))
                if int(button.text()) == self.current_page:
                    button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#ACACAC;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)
                else:
                    button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#4E4E4E;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)

    def pagePrev(self):
        limit = 1
        if int(self.button1.text()) > limit:
            start_page = int(self.button4.text())-4 #pls help, i dunno what to do anymore
            for i, button in enumerate(self.buttons, start=start_page):
                button.setText(str(i)) #WHY THE HELL I NEED TO DO DIFFERENTLY FOR THIS
                if int(button.text()) == self.current_page:
                    button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#ACACAC;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)
                else:
                    button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#4E4E4E;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)


    def pageEnd(self):
        self.loadSQLWorker()
        self.current_page = self.total_page

        self.worker = WorkerThread(self.total_page-1, 25) #page number,limit
        self.worker.start()
        self.worker.result.connect(self.handle_result)
        for i, button in enumerate(self.buttons, start=self.total_page-3):
            button.setText(str(i))
            if int(button.text()) == self.current_page:
                button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#ACACAC;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)
            else:
                button.setStyleSheet("""
                        QPushButton { 
                            color:white; 
                            background-color:#4E4E4E;
                            border:2px solid;
                            padding: 0 8px;
                            border-right:0px;
							border-left:0px;
                            }
                        QPushButton:disabled { 
                            color: rgba(0,0, 0, 100);
                            }
                        
                        QPushButton:hover:!pressed { 
                            background-color: #262626;
                            border-style:inset;
                            }
                        QPushButton:hover {
                            background-color:#171717;
                            }
                        QPushButton:hover {
                            background-color:rgb(61, 61, 61);
                            }
                        """)
        
       
      
class Add(QWidget):
    def __init__(self, parent):
        super(Add, self).__init__()
        
        
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/addStok.ui", self)
        self.parent = parent
        self.apply.clicked.connect(self.Add_Action)
        self.kodebarang.lineEdit().setPlaceholderText("Pilih Kode Barang")
        self.lokasi.lineEdit().setPlaceholderText("Pilih Rak Barang")
        self.satuan_jumlah.setPlaceholderText("Pilih Satuan Jumlah")

        model = QStandardItemModel()
        model_lokasi = QStandardItemModel()
        

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT id_katalog, kodebarang, nama_barang, spesifikasi, satuan_jumlah FROM daftar_katalog;")
        self.myresult = mycursor.fetchall() #make a qcompleter, IT SUPPOSED TO BE A FUNCTION BUT ATTRIBUTE ERRO
        mycursor.close()
        mydb.close()

        for kodebarang in self.myresult:
            self.kodebarang.addItem(kodebarang[1], kodebarang[0])

        for i,word in enumerate(self.myresult):
            item = QStandardItem(word[1])
            model.setItem(i, 0, item)

        completer = QCompleter(self) 
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        self.kodebarang.setCompleter(completer)
        self.kodebarang.setSourceModel(model)


        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id, lokasi FROM lokasi WHERE deleted_At is NULL;")
        self.myresult_lokasi = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        

        for lokasi in self.myresult_lokasi:
            self.lokasi.addItem(lokasi[1], lokasi[0])
    

        for i,word in enumerate(self.myresult_lokasi):
            item = QStandardItem(word[1])
            model_lokasi.setItem(i, 0, item)

        completer_lokasi = QCompleter(self) 
        completer_lokasi.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer_lokasi.setCaseSensitivity(Qt.CaseInsensitive)
        completer_lokasi.setCompletionMode(QCompleter.PopupCompletion)
        
        self.lokasi.setCompleter(completer_lokasi)
        self.lokasi.setSourceModel(model_lokasi)

        self.kodebarang.installEventFilter(self)
        self.lokasi.installEventFilter(self)
       

        self.kodebarang.setCurrentIndex(-1)
        
        self.kodebarang.currentIndexChanged.connect(self.namaLabel)

    def eventFilter(self, source, event): #TODO: just another dream not realized
        if event.type() == QEvent.FocusIn and source == self.kodebarang :
            self.kodebarang.showPopup()
            if event.type() == QEvent.FocusOut:
                self.kodebarang.hidePopup()

        elif event.type() == QEvent.FocusIn and source == self.lokasi:
            self.lokasi.showPopup()
            if event.type() == QEvent.FocusOut:
                self.lokasi.hidePopup()
            
        return super().eventFilter(source, event)
       
    def namaLabel(self, value):
        try:
            self.nama_barang.setText(self.myresult[value][2])
            self.spesifikasi.setText(self.myresult[value][3])
            self.satuan_jumlah.setText(self.myresult[value][4])
        except IndexError:
            print("Index out of bounds")
        
    def Add_Action(self):
        jumlahbarang = abs(int(self.jumlah.text()))

        push = []
        push.insert(0, self.kodebarang.currentData())
        push.insert(1, jumlahbarang)
        push.insert(2, self.keterangan.text())
        push.insert(3, self.lokasi.currentData())

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        error = connection.Error()
        app = MyApp.instance()
        user_id = app.id

        try:
            query = "INSERT INTO stok (id_katalog, status, keterangan, id_lokasi, created_At, created_By) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(query, (push[0], push[1], push[2], push[3], datetime.now(timezone('Asia/Jakarta')), user_id))    
            mydb.commit()
            mycursor.close()
            mydb.close()
        except error as err: 
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong{}".format(err))
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
            self.parent.stock_change.emit(42)
            self.close()

        

class Remove(QWidget):
    def __init__(self, parent):
        super(Remove, self).__init__()
        
        
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/addStok.ui", self)
        self.setWindowTitle("Barang Keluar")
        self.parent = parent
        self.apply.clicked.connect(self.Add_Action)
        self.kodebarang.lineEdit().setPlaceholderText("Pilih Kode Barang")
        self.lokasi.lineEdit().setPlaceholderText("Pilih Rak Barang")
        self.lokasi.setEnabled(False)
        self.satuan_jumlah.setPlaceholderText("Pilih Satuan Jumlah")

        model = QStandardItemModel()
        model_lokasi = QStandardItemModel()
        
        

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT id_katalog, kodebarang, nama_barang, spesifikasi, satuan_jumlah FROM daftar_katalog;")
        self.myresult = mycursor.fetchall() #make a qcompleter, IT SUPPOSED TO BE A FUNCTION BUT ATTRIBUTE ERRO
        mycursor.close()
        mydb.close()

        for kodebarang in self.myresult:
            self.kodebarang.addItem(kodebarang[1], kodebarang[0])

        for i,word in enumerate(self.myresult):
            item = QStandardItem(word[1])
            model.setItem(i, 0, item)

        completer = QCompleter(self) 
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        
        self.kodebarang.setCompleter(completer)
        self.kodebarang.setSourceModel(model)


        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id, lokasi FROM lokasi WHERE deleted_At is NULL;")
        self.myresult_lokasi = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        

        for lokasi in self.myresult_lokasi:
            self.lokasi.addItem(lokasi[1], lokasi[0])
    

        for i,word in enumerate(self.myresult_lokasi):
            item = QStandardItem(word[1])
            model_lokasi.setItem(i, 0, item)

        completer_lokasi = QCompleter(self) 
        completer_lokasi.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer_lokasi.setCaseSensitivity(Qt.CaseInsensitive)
        completer_lokasi.setCompletionMode(QCompleter.PopupCompletion)
        
        self.lokasi.setCompleter(completer_lokasi)
        self.lokasi.setSourceModel(model_lokasi)




        

       

        self.kodebarang.installEventFilter(self)
        self.lokasi.installEventFilter(self)

        self.kodebarang.setCurrentIndex(-1)
        
        self.kodebarang.currentIndexChanged.connect(self.namaLabel)

    def eventFilter(self, source, event): #TODO: just another dream not realized
        if event.type() == QEvent.FocusIn and source == self.kodebarang :
            self.kodebarang.showPopup()
            if event.type() == QEvent.FocusOut:
                self.kodebarang.hidePopup()

        elif event.type() == QEvent.FocusIn and source == self.lokasi:
            self.lokasi.showPopup()
            if event.type() == QEvent.FocusOut:
                self.lokasi.hidePopup()
            
        return super().eventFilter(source, event)
       
    def namaLabel(self, value):
        try:
            print(self.myresult[value][0])
            self.nama_barang.setText(self.myresult[value][2])
            self.spesifikasi.setText(self.myresult[value][3])
            self.satuan_jumlah.setText(self.myresult[value][4])
            self.lokasi.setEnabled(True)

            model_lokasi = QStandardItemModel()
            mydb = connection.Connect()
            mycursor = mydb.cursor()
            mycursor.execute("SELECT DISTINCT id_lokasi, lokasi FROM katalog_jakarta.daftar_stok WHERE id_katalog = %s;", (self.myresult[value][0],))
            self.myresult_lokasi = mycursor.fetchall()
            mycursor.close()
            mydb.close()
            
            self.lokasi.clear()
            for lokasi in self.myresult_lokasi:
                self.lokasi.addItem(lokasi[1], lokasi[0])
        

            for i,word in enumerate(self.myresult_lokasi):
                item = QStandardItem(word[1])
                model_lokasi.setItem(i, 0, item)

            self.lokasi.setSourceModel(model_lokasi)
        except IndexError:
            print("Index out of bounds")
        
    def Add_Action(self):
        jumlahbarang = -abs(int(self.jumlah.text()))

        push = []
        push.insert(0, self.kodebarang.currentData())
        push.insert(1, jumlahbarang)
        push.insert(2, self.keterangan.text())
        push.insert(3, self.lokasi.currentData())

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        error = connection.Error()
        app= MyApp.instance()
        user_id = app.id
        try:
            
            query = "INSERT INTO stok (id_katalog, status, keterangan, id_lokasi, created_At, created_By) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(query, (push[0], push[1], push[2], push[3], datetime.now(timezone('Asia/Jakarta')), user_id))    
            mydb.commit()
            mycursor.close()
            mydb.close()
        except error as err: 
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong. Error : {}".format(err))
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
            self.parent.stock_change.emit(42)
            self.close()

class Edit(QWidget):
    def __init__(self, parent):
        super(Edit, self).__init__()
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/editStok.ui", self)

        self.parent = parent
        self.apply.clicked.connect(lambda:self.Edit_Action(self.edit_array[0]))
        
        self.loadData()
        self.setWindowTitle("Ubah Stok Barang")
        self.kodebarang.currentIndexChanged.connect(self.namaLabel)
    


    def loadData(self): 
        self.edit_array = self.parent.singleClick()
        
        model = QStandardItemModel()
        model_lokasi = QStandardItemModel()


        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT id_katalog, kodebarang, nama_barang, spesifikasi, satuan_jumlah FROM daftar_katalog;")
        self.myresult = mycursor.fetchall() 
        mycursor.close()
        mydb.close()
        
        

        for kodebarang in self.myresult:
            self.kodebarang.addItem(kodebarang[1], kodebarang[0])
    
        for i,word in enumerate(self.myresult):
            if int(word[0]) == int(self.edit_array[1]) :
                self.kodebarang.setCurrentIndex(i)
                self.nama_barang.setText(word[2])
                self.spesifikasi.setText(word[3])
                self.satuan_jumlah.setText(word[4])
    
            item = QStandardItem(word[1])
            model.setItem(i, 0, item)

        completer = QCompleter(self) 
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        
        self.kodebarang.setCompleter(completer)
        self.kodebarang.setSourceModel(model)


        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id, lokasi FROM lokasi;")
        self.myresult_lokasi = mycursor.fetchall() 
        mycursor.close()
        mydb.close()
        for lokasi in self.myresult_lokasi:
            if int(word[0]) == int(self.edit_array[2]) :
                self.lokasi.setCurrentIndex(i)
            self.lokasi.addItem(lokasi[1], lokasi[0])
    

        for i,word in enumerate(self.myresult_lokasi):
            item = QStandardItem(word[1])
            model_lokasi.setItem(i, 0, item)

        completer_lokasi = QCompleter(self) 
        completer_lokasi.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer_lokasi.setCaseSensitivity(Qt.CaseInsensitive)
        completer_lokasi.setCompletionMode(QCompleter.PopupCompletion)
        
        self.lokasi.setCompleter(completer_lokasi)
        self.lokasi.setSourceModel(model_lokasi)




        

        self.kodebarang.installEventFilter(self)
        self.lokasi.installEventFilter(self)
      
        self.kodebarang.currentIndexChanged.connect(self.namaLabel)
        self.barang_masuk.stateChanged.connect(self.checkboxState)
        self.barang_keluar.stateChanged.connect(self.checkboxState)

        self.kodebarang.lineEdit().setPlaceholderText("Pilih Kode Barang")
        self.lokasi.lineEdit().setPlaceholderText("Pilih Rak Barang")


        #LOAD ALL DATA TO TEXTBOX
        jumlah = self.edit_array[7].split()[0]
        if int(jumlah) > 0:
            self.barang_masuk.setChecked(True)
        elif int(jumlah) <0 :
            self.barang_keluar.setChecked(True)
        self.jumlah.setText(str(abs(int(jumlah)))) #FORGIVE ME FATHER
    
        self.keterangan.setText(self.edit_array[8])
        


    def eventFilter(self, source, event): #TODO: just another dream not realized
        if event.type() == QEvent.FocusIn and source == self.kodebarang :
            self.kodebarang.showPopup()
            if event.type() == QEvent.FocusOut:
                self.kodebarang.hidePopup()

        elif event.type() == QEvent.FocusIn and source == self.lokasi:
            self.lokasi.showPopup()
            if event.type() == QEvent.FocusOut:
                self.lokasi.hidePopup()

        elif event.type() == QEvent.FocusIn and source == self.satuan_jumlah:
            self.satuan_jumlah.showPopup()
            if event.type() == QEvent.FocusOut:
                self.satuan_jumlah.hidePopup()
            
        return super().eventFilter(source, event)

    def namaLabel(self, value):
        self.nama_barang.setText(self.myresult[value][2])
        self.spesifikasi.setText(self.myresult[value][3])
        self.satuan_jumlah.setText(self.myresult[value][4])
    

    def checkboxState(self,state):
        sender = self.sender()

        if sender == self.barang_masuk and state == 2:  # 2 corresponds to checked state
            self.barang_keluar.setChecked(False)

        elif sender == self.barang_keluar and state == 2:
            self.barang_masuk.setChecked(False)



    def Edit_Action(self, id):
        if self.barang_keluar.isChecked():
            jumlah = -abs(int(self.jumlah.text()))

        elif self.barang_masuk.isChecked():
            jumlah = abs(int(self.jumlah.text()))
        push = []
        push.insert(0, id)
        push.insert(1, self.kodebarang.currentData())
        push.insert(2, jumlah)
        push.insert(3, self.keterangan.text())
        push.insert(4, self.lokasi.currentData())

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        
       
        query = "UPDATE stok SET id_katalog = %s, status = %s , keterangan = %s, id_lokasi = %s WHERE id = %s "

        try:
            mycursor.execute(query, (push[1], push[2], push[3], push[4], push[0]))    
            mydb.commit()
            mycursor.close()
            mydb.close()
        except: 
            msgBox1 = QMessageBox()
            msgBox1.setText("Ada data yang kosong atau salah")
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
            self.parent.stock_change.emit(42)
            self.close()

    
    



        
        

       

       

