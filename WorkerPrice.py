from PyQt5.QtCore import QObject, pyqtSignal, QThread
from styleframe import StyleFrame, Styler, utils
import connection,os,math



class WorkerThread(QThread):
    result = pyqtSignal(list)

    def __init__(self, page_number, limit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_number = page_number
        self.limit = limit

    def run(self):
        offset = self.page_number * self.limit
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        query = "SELECT  id_katalog, id_merek, id_satuan_ukur , id_satuan_jumlah, kodebarang, nama_barang,  nama_merek, spesifikasi, satuan_jumlah, harga_barang FROM price_list LIMIT 25 OFFSET %s;"
        mycursor.execute(query, (offset,))
        myresult = mycursor.fetchall()
        self.result.emit(myresult)

    def stop(self):
        if self.isRunning() :
            self.quit()
            self.wait()

class WorkerPage(QThread):
    data_emitted = pyqtSignal(int,int) #emit total_page and total_query

    def run(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT total_pricelist, pricelist_page FROM Count_Query;")
        myresult = mycursor.fetchall()
        self.data_emitted.emit(myresult[0][0], int(myresult[0][1]))

    def stop(self):
        if self.isRunning() :
            self.quit()
            self.wait()

