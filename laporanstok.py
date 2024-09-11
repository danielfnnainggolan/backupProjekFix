from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QDialog, QMessageBox,QCompleter, QTreeView
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QColor, QPainter
from PyQt5 import uic
from datetime import datetime
from PyQt5.QtCore import Qt
import connection, os, resources





class LaporanStokFunction(QMainWindow):
    def __init__(self):
        super(LaporanStokFunction, self).__init__()
        uic.loadUi("ui/laporanstok.ui", self)
        # self.stokTable.setColumnHidden(0, True)
        # self.stokTable.setColumnHidden(1, True)
        # self.stokTable.setColumnHidden(2, True)
        # self.stokTable.setColumnHidden(3, True)
        self.loadData()
        self.searchField.textChanged.connect(self.search)
        self.stokTable.setColumnHidden(1, 1)
        self.checker = False

        # self.worker_thread = WorkerThread()
        # self.worker_thread.data_added.connect(self.refreshData)
        
      
    def loadData(self):
       
        mydb = connection.Connect()
        self.stokTable.setModel(None)
        mycursor = mydb.cursor()
        mycursor.execute("select id_katalog, kodebarang, nama_barang, nama_merek, jumlah , lokasi FROM laporan ")
        self.myresult_parent = mycursor.fetchall()
        mycursor.close()
        mydb.close()

        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("select id_katalog, kodebarang, nama_barang, nama_merek, jumlah, lokasi, id_stok, keterangan FROM daftar_stok")
        self.myresult_child = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        self.importData(self.myresult_parent, self.myresult_child)
        
       
    def importData(self, data_parent, data_child, root=None):
        self.model = QStandardItemModel()
        self.model.setRowCount(0)
        self.model.setColumnCount(6)


        self.model.setHorizontalHeaderLabels(['No.', 'id_katalog',  'Kode Barang', 'Nama Barang', 'Nama Merek', 'Jumlah', 'Lokasi', 'Keterangan'])

        if root is None:
            root = self.model.invisibleRootItem()
                
        count_parent = 1
        count_child = 1

        for parent in data_parent:
            
            parentItem = root
            item_parent = QStandardItem(str(parent[0]))
            parent_id = parent[0]
            item_c0 = QStandardItem(str(count_parent))
            item_c1 = QStandardItem(str(parent[1]))
            item_c2 = QStandardItem(parent[2])
            item_c3 = QStandardItem(parent[3])
            item_c4 = QStandardItem(str(parent[4]))
            item_c5 = QStandardItem(parent[5])
            parentItem.appendRow([item_c0, item_parent, item_c1, item_c2, item_c3, item_c4, item_c5 ])
            parentItem = item_c0
            
            for child in data_child:
                child_id = child[0]
                item_child = QStandardItem(str(child[0]))
                if parent_id == child_id : #cc= column child
                    item_cc0 = QStandardItem(str(count_child))
                    item_cc1 = QStandardItem(child[1])
                    item_cc2 = QStandardItem(child[2])
                    item_cc3 = QStandardItem(child[3])
                    item_cc4 = QStandardItem(str(child[4]))
                    item_cc5 = QStandardItem(child[5])
                    item_cc6 = QStandardItem(child[7])
                    parentItem.appendRow([ item_cc0, item_child, item_cc1, item_cc2, item_cc3, item_cc4, item_cc5, item_cc6])
                    count_child+=1
                else:
                    count_child = 1
                    continue

            count_parent+=1
            
                # else:
                #     continue
                

        self.stokTable.setModel(self.model)
       
    def search(self):
       
        search = str(self.searchField.text().lower())

        myresult_parent = [
            x
            for x in self.myresult_parent
            if search in str(x[1].lower())
            or search in str(x[2].lower())
            or search in str(x[3].lower())
            or search in str(x[5].lower())
            or search in str(x[6].lower())
        ]
        
        self.model.setRowCount(0)
        self.importData(myresult_parent, self.myresult_child)
        


        
        

       

       

