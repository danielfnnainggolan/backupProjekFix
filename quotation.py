from PyQt5.QtWidgets import QWidget,  QTableWidgetItem, QMainWindow, QMessageBox,QCompleter, QHeaderView, QFileDialog
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtCore import Qt, QEvent, QTimer
import connection, os, dashboard
from Worker import WorkerSearch, WorkerExport
from WorkerPrice import WorkerPageQuotation, WorkerQuotation

from pytz import timezone


class QuotationFunction(QWidget):
    def __init__(self):
        super(QuotationFunction, self).__init__()
        uic.loadUi("ui/quotationList.ui", self)
        self.total_page = None
        self.total_query = None
        self.workerSearch = None
        self.worker = None
        self.workerPage = None
        self.loadPageWorker()
        
        self.loadModel = QStandardItemModel()
        
        self.loadModel.setHorizontalHeaderItem(0, QStandardItem("id"))
        self.loadModel.setHorizontalHeaderItem(1, QStandardItem("Nama"))
        self.loadModel.setHorizontalHeaderItem(2, QStandardItem("Alamat"))
        self.loadModel.setHorizontalHeaderItem(3, QStandardItem("Nomor HP"))
        self.loadModel.setHorizontalHeaderItem(4, QStandardItem("Email"))
        
        
        self.editButton.setEnabled(False)
        self.deleteButton.setEnabled(False)
        self.customerTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.customerTable.clicked.connect(self.singleClick)
        # self.customerTable.itemDoubleClicked.connect(self.doubleclick)

        self.current_page = 1
        self.limit_count = 25
        self.loadDataWorker()
        
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.loadSearchWorker)

        self.searchField.textChanged.connect(self.text_changed)

        
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

        self.addButton.clicked.connect(self.Addfunction)
        self.editButton.clicked.connect(self.Editfunction)
        self.deleteButton.clicked.connect(self.Deletefunction)
        self.purchase_order.clicked.connect(self.Exportfunction)
    
    def text_changed(self):
        if self.search_timer.isActive():
            self.search_timer.stop()

        # Restart the timer to debounce input
        self.search_timer.start(300)

    def Deletefunction(self):
        self.customerTable.clearSelection()
        msgBox = QMessageBox()
        msgBox.setText("Apakah Anda yakin untuk menghapus harga ini ?")
        msgBox.setInformativeText("Nama Barang : "+" "+self.data[4])

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
            mycursor.execute("UPDATE katalog SET harga = 0 WHERE id_katalog= %s ;", self.data[0])
            mydb.commit()
            mycursor.close()
            mydb.close()
            
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil dihapus")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            ret1 = msgBox1.exec()
            self.loadSQLWorker()
            self.pageStart()
    
    #Worker Start
    def closeEvent(self, event):
        # Make sure to stop the worker thread when closing the application
        if self.workerSearch is not None:
            if self.workerSearch.isRunning():
                self.workerSearch.stop()

        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.stop()

        if self.workerPage is not None:
            if self.workerPage.isRunning():
                self.workerPage.stop()

        super().closeEvent(event)

    def loadDataWorker(self):
        if self.worker is not None:
            if self.worker.isRunning():
                self.worker.stop()

        self.worker = WorkerQuotation(0,25)
        self.worker.result.connect(self.handle_result)
        self.worker.finished.connect(lambda :self.cleanup_worker(self.worker))
        self.worker.start()

    def loadPageWorker(self):
        if self.workerPage is not None:
            if self.workerPage.isRunning():
                self.workerPage.stop()

        self.workerPage = WorkerPageQuotation()
        self.workerPage.data_emitted.connect(self.handle_sql_result)
        self.workerPage.finished.connect(lambda : self.cleanup_worker(self.workerPage))
        self.workerPage.start()

    def loadSearchWorker(self):
        search_query = self.searchField.text()
        if self.workerSearch is not None:
            if self.workerSearch.isRunning():
                self.workerSearch.stop()

        self.workerSearch = WorkerSearch(search_query)
        self.workerSearch.data_emitted.connect(self.handle_search_result)
        self.workerSearch.finished.connect(lambda : self.cleanup_worker(self.workerSearch))
        self.workerSearch.start()

    def cleanup_worker(self, worker_name):
        if worker_name == self.worker:
            self.worker = None
        elif worker_name == self.workerPage:
            self.workerPage = None
        elif worker_name == self.workerSearch:
            self.workerSearch = None

    def handle_result(self, result):
        self.loadData(result)

    def handle_search_result(self, data_emitted):
        self.loadData(data_emitted)
    
    def handle_sql_result(self, total_query, total_page):
        self.total_query = total_query
        self.total_page = total_page
        if total_page == 0:
            self.end.setEnabled(False)
            self.next.setEnabled(False)
            self.previous.setEnabled(False)
            self.start.setEnabled(False)
            self.current_page = 0
        else:
            self.end.setEnabled(True)
            self.next.setEnabled(True)
            self.previous.setEnabled(True)
            self.start.setEnabled(True)
            self.current_page = 1
        self.jumlah_halaman.setText("Halaman %s dari %s halaman" %(self.current_page, total_page))
        
    def pageClicked(self, page_number, limit):
        self.current_page = page_number
        page_number-=1
        self.worker = WorkerQuotation(page_number, limit)
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
        self.current_page = 1
        self.worker = WorkerQuotation(0, 0)
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
        self.current_page = self.total_page

        self.worker = WorkerQuotation(self.total_page-1, 25) #page number,limit
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

    
    

    def closeEvent(self, event):
        self.window = QMainWindow()
        self.ui = dashboard()
        self.ui.show()
        event.accept()

    def Addfunction(self):
        self.add_child = Add(parent=self)
        self.add_child.show()
        
    def Editfunction(self):
        self.edit_child = Edit(parent=self)
        self.edit_child.show()

    def Exportfunction(self):
        file_path = self.openFileNameDialog()
        file_path = file_path.split(".xlsx")[0]
        self.export_child = Export(file_path, parent=self)
        self.export_child.show()
        


    # def doubleclick(self):  # popup for images
    #     #hopefully
    #     self.preview = QDialog(self)
    #     self.preview.setWindowTitle("Preview Image")
    #     self.pixmap = QPixmap((os.path.join("data/uploads/", self.data[6])))
    #     self.preview.label = QLabel(self.preview)


    #     self.preview.label.setPixmap(self.pixmap)
    #     self.preview.label.resize(self.pixmap.width(),
    #                       self.pixmap.height())
    #     self.preview.show()

    def singleClick(self,index):  # enable edit button get item
        self.editButton.setEnabled(True)
        self.deleteButton.setEnabled(True)
        self.data = []
        row = index.row()
        for x in range(self.loadModel.columnCount()):
            self.data.insert(x, self.loadModel.item(row, x).text())
        # return self.data
        
    def delete(self):
        self.purchase_order.setEnabled(False)
        
    def loadData(self, myresult):
        
        row = 0
        self.loadModel.setRowCount(len(myresult))
        for katalog in myresult:
            for col, value in enumerate(katalog):
                item = QStandardItem(str(value) if col != 9 else str(f'{value:,}').rstrip("0").rstrip("."))
                item.setTextAlignment(Qt.AlignCenter)
                self.loadModel.setItem(row, col, item)
            row += 1
        
        self.customerTable.setModel(self.loadModel)
        self.customerTable.setColumnHidden(0, 1)
        
        
        

       
        
        

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Save Excel File",
            "C:",
            "Excel File (*.xlsx)",
            options=options,
        )
        if fileName:
            return fileName
        else:
            return ""
        
    
    def Deletefunction(self):
        self.customerTable.clearSelection()
        msgBox = QMessageBox()
        msgBox.setText("Apakah Anda yakin untuk menghapus data ini ?")
        msgBox.setInformativeText("Nama Barang : "+" "+self.data[4])

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
            mycursor.execute("UPDATE katalog SET deleted_At = %s WHERE id_katalog= %s ;", (datetime.now(timezone('Asia/Jakarta')), self.data[0]))
            mydb.commit()
            mycursor.close()
            mydb.close()
            
            self.editButton.setEnabled(False)
            self.deleteButton.setEnabled(False)
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil dihapus")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            ret1 = msgBox1.exec()
            self.loadPageWorker()
            self.pageStart()
        


    def search(self, data_emitted):

        
        row = 0
        self.loadModel.setRowCount(len(data_emitted))
        for katalog in data_emitted:
            self.loadModel.setItem(row, 0, QStandardItem(str(katalog[0])))
            self.loadModel.setItem(row, 1, QStandardItem(str(katalog[1])))
            self.loadModel.setItem(row, 2, QStandardItem(str(katalog[2])))
            self.loadModel.setItem(row, 3, QStandardItem(str(katalog[3])))
            self.loadModel.setItem(row, 4, QStandardItem(katalog[4]))
            self.loadModel.setItem(row, 5, QStandardItem(katalog[5]))
            self.loadModel.setItem(row, 6, QStandardItem(katalog[6]))
            self.loadModel.setItem(row, 7, QStandardItem(katalog[7]))
            self.loadModel.setItem(row, 8, QStandardItem(katalog[8]))

            row += 1

        self.customerTable.setModel(self.loadModel)
        self.customerTable.setColumnHidden(0, 1)
        self.customerTable.setColumnHidden(1, 1)
        self.customerTable.setColumnHidden(2, 1)
        self.customerTable.setColumnHidden(3, 1)

        
class Edit(QWidget):  ##Edit Katalog 
    def __init__(self, parent):
        
        super(Edit, self).__init__()
        uic.loadUi("ui/editPrice.ui", self)
        
        self.parent = parent
        self.data = self.parent.data
        self.apply.clicked.connect(lambda:self.auth(self.data[0]))
        print(self.data)
        self.setWindowTitle("Ubah Harga Barang")



        model = QStandardItemModel()

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT id_katalog , kodebarang FROM katalog where deleted_At is NULL")
        self.myresult = mycursor.fetchall()      
        mycursor.close()  
        mydb.close()
        

        for katalog in self.myresult:
            self.kodebarang.addItem(katalog[1], katalog[0])
    

        for i,word in enumerate(self.myresult):
            item = QStandardItem(word[1])
            model.setItem(i, 0, item)
            if word[0] == int(self.data[0]):
                self.kodebarang.setCurrentIndex(i)

        completer = QCompleter(self) 
        completer.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        
        self.kodebarang.setCompleter(completer)
        self.kodebarang.setSourceModel(model)
        self.harga.setValue(int(self.data[9].replace(",", "")))
        self.nama_barang.setText(self.data[5])
        self.spesifikasi.setText(self.data[7])
        self.satuan_jumlah.setText(self.data[8])
        
        
  

   
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Images",
            "",
            "Image Files (*.jpg *.png)",
            options=options,
        )
        if fileName:
            nameFile = fileName.split("/")
            self.image.setText(nameFile[-1])
            self.file_path = fileName

    def auth(self, id):
        push = []
        push.insert(0, self.harga.cleanText().replace('.', ''))
        push.insert(1, id)
        
        
        mydb = connection.Connect()
        error = connection.Error()
        mycursor = mydb.cursor()
        try:
            query = "UPDATE katalog SET harga = %s WHERE id_katalog = %s "
            mycursor.execute(query, (push[0],push[1]))    
            mydb.commit()
            mycursor.close()
            mydb.close()
        #winsoft 24*14
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
        
        self.parent.loadPageWorker()
        self.parent.pageStart()
        self.close()
        
        # if "/" in self.file_path:
        #     nameFile = self.file_path.split("/")
        # else:
        #     nameFile = self.file_path
        # if "." in nameFile[1]:
        #     nameFile = nameFile[1].split(".")
        # QFile.copy(self.file_path, os.path.join("data/uploads", str(push[1])+"."+str(nameFile[-1])))
        # print(self.file_path)
        # push.insert(8,str(push[1])+"."+str(nameFile[-1]))
        
        
class Export(QWidget):  ##Export Function
    def __init__(self, file_path, parent):
        super(Export, self).__init__()
        uic.loadUi("ui/export.ui", self)
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.progressBar.setRange(0, 100)
        self.file_path = file_path
        self.progressBar.setValue(0)
        self.start_export()

    def start_export(self):
        self.workerExport = WorkerExport(self.file_path)
        self.workerExport.progressBar.connect(self.update_progress)
        self.workerExport.finished.connect(self.cleanup_worker)
        self.workerExport.start()
        

    def cleanup_worker(self):
        self.workerExport = None

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()

    def update_progress(self, progress):
        
            
        
        self.progressBar.setValue(progress)
        if self.progressBar.value() == 100:
            print("YAY")
            msgBox1 = QMessageBox()
            msgBox1.setText("Data berhasil diekspor")
            msgBox1.setIcon(QMessageBox.Information)
            msgBox1.setStandardButtons(QMessageBox.Ok)
            msgBox1.setWindowIcon(QIcon(os.path.join("data/ui/", "logo.png")))
            msgBox1.setWindowTitle("Pemberitahuan")
            ret1 = msgBox1.exec()
            self.close()
            
class Add(QWidget):
    def __init__(self, parent):
        super(Add, self).__init__()
        self.setWindowFlags(self.windowFlags()^ Qt.WindowContextHelpButtonHint)
        uic.loadUi("ui/addCustomer.ui", self)
        self.parent = parent
        self.setWindowTitle("Tambah Data Pelanggan")
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
            mycursor.execute(query, (push[0], push[1], push[2], push[3], datetime.now(timezone('Asia/Jakarta'))))    
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
            self.parent.loadPageWorker()
            self.parent.pageStart()
            self.close()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        