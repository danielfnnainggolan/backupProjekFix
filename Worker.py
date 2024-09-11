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
        query = "SELECT  id_katalog, id_merek, id_satuan_ukur , id_satuan_jumlah, kodebarang, nama_barang,  nama_merek, spesifikasi, satuan_jumlah FROM daftar_katalog LIMIT 25 OFFSET %s;"
        mycursor.execute(query, (offset,))
        myresult = mycursor.fetchall()
        self.result.emit(myresult)

    def stop(self):
        if self.isRunning() :
            self.quit()
            self.wait()

class WorkerSQL(QThread):
    data_emitted = pyqtSignal(int,int) #emit total_page and total_query

    def run(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT total_katalog, katalog_page FROM Count_Query;")
        myresult = mycursor.fetchall()
        self.data_emitted.emit(myresult[0][0], int(myresult[0][1]))

    def stop(self):
        if self.isRunning() :
            self.quit()
            self.wait()

class WorkerSearch(QThread):
    data_emitted = pyqtSignal(list) #emit total_page and total_query

    def __init__(self, search_query):
        super().__init__()
        self.search_query = search_query
        self._is_running = True
        self.timer = None
    
    def run(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT  id_katalog, id_merek, id_satuan_ukur , id_satuan_jumlah, kodebarang, nama_barang,  nama_merek, spesifikasi, satuan_jumlah  FROM daftar_katalog;"
        )
        myresult = mycursor.fetchall()

        search = str(self.search_query.lower())


        myresult = [                   #what is this fucking called? list compherehension
            x
            for x in myresult
            if search in x[3].lower()
            or search in x[4].lower()
            or search in x[5].lower()
            or search in x[6].lower()
            or search in x[7].lower()
        ]

        
        self.data_emitted.emit(myresult[:25])

    def stop(self):
        if self.isRunning() :
            self.quit()
            self.wait()

class WorkerExport(QThread):
    progressBar = pyqtSignal(int) #emit total_page and total_query
    def __init__(self, path_file):
        super().__init__()
        self.path_file = path_file
    
    def run(self):
        mydb = connection.Connect()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT kodebarang, nama_barang, nama_merek, spesifikasi FROM daftar_katalog;")
        myresult = mycursor.fetchall()
        rowCount = len(myresult)


        
        
        columnsHeader = ["No", "Nomor Katalog", "Nama Barang", "Merek Barang", "Spesifikasi"]

        columnCount = 5
        data = {}
        items_processed = 0
        percent_completed = 0
        columncounter = 0
        total_item = rowCount*columnCount
        for column in range(columnCount):
            columnData = []
            for row in range(rowCount):
                items_processed+=1
                if column == 0:
                    columnData.append(row+1) 
                    continue
                item = myresult[row][column-1]
                columnData.append(item)
                
                
                
            percent_completed = math.floor(items_processed /total_item * 100)
            self.progressBar.emit(percent_completed)
            data.update({columnsHeader[columncounter] : columnData})
            columncounter+=1

        
        sf = StyleFrame(data)
        sf.apply_column_style(styler_obj=Styler(font="Calibri", font_size=10), cols_to_style=columnsHeader)
        sf.apply_headers_style(styler_obj=Styler(font="Calibri", font_size=15.0),cols_to_style=columnsHeader,)
        
        
        if self.path_file :
            ew = StyleFrame.ExcelWriter((os.path.join(self.path_file+".xlsx")))
            sf.to_excel(ew, sheet_name="Katalog", best_fit=columnsHeader)
            ew.close()
            

    def stop(self):
        if self.isRunning() :
            self.quit()
            self.wait()
        
        
        
        