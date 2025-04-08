
from PyQt5.QtWidgets import QTreeView, QCompleter, QComboBox, QDoubleSpinBox
from PyQt5.QtCore import Qt, QRect, QSortFilterProxyModel, QRegExp, QLocale

class CustomComboBox(QComboBox):
   
    def __init__(self, parent = None):
        super(CustomComboBox, self).__init__(parent)
        self.c = None
        self.setInsertPolicy(QComboBox.NoInsert)
        self.text = "" # I DONT KNOW OTHER WAY TO DO IT THIS IS THE ONLY WAY I KNOW 
        self.currentTextChanged.connect(self.FilterIt)
        self.proxyModel = None

    def FilterIt(self, text):
        if self.proxyModel:
            self.c.complete(QRect())
            

        
    def setCompleter(self, completer):
        if self.c:
            self.c.disconnect(self)

        self.c = completer
    
        if not self.c:
            return

        self.c.setWidget(self)
        self.c.setCompletionMode(QCompleter.PopupCompletion)
        self.c.setCaseSensitivity(Qt.CaseInsensitive)
        self.c.setModelSorting(QCompleter.CaseInsensitivelySortedModel)
        self.c.activated[str].connect(self.insertCompletion)
            
    def insertCompletion(self, completion):
        proxy_model = self.c.completionModel()
        source_model = proxy_model.sourceModel() if proxy_model else None
    
        if source_model:
            matched_index = source_model.index(0, 0)
            matches = source_model.match(matched_index, Qt.DisplayRole, completion, -1, Qt.MatchExactly)
    
        if matches:
            index = proxy_model.mapFromSource(matches[0])
            self.setCurrentIndex(index.row())

        self.setEditText(completion)
        self.hidePopup()
        
    def completer(self):
        return self.c
    
    def showPopup(self):
        self.text = self.currentText()
        self.c.complete()

    def hidePopup(self):
        if self.c and self.c.popup().isVisible():
            # self.c.complete(QRect())
            self.c.popup().hide()
        
    def setSourceModel(self, source_model):
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(source_model)
        self.setModel(self.proxyModel)
        
    def setModel(self, model):
        if self.c:
            self.c.setModel(model)

    def keyPressEvent(self, e):
        if self.c and self.c.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Shift, Qt.Key_CapsLock):
                e.ignore()
                return  
        elif self.c and self.currentText() == "":
            self.showPopup()

        

        if e.key() == Qt.Key_Backspace:
            self.text = self.text[:-1]
        else:
            self.text+=e.text()

        if self.proxyModel:
            self.proxyModel.setFilterRegExp(QRegExp(self.text, Qt.CaseInsensitive, QRegExp.FixedString))  
        
        super().keyPressEvent(e)

class CustomSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setLocale(QLocale(QLocale.English))
        
    def textFromValue(self, value):
        # Format the value using the current locale (adds thousand separator)
        if value == 0:
            return ""
        else: 
            formatted_value = self.locale().toString(value, 'f', self.decimals())
            return formatted_value
    

    def focusInEvent(self, event):
        super().focusInEvent(event)
        
        # Move the cursor position to after the prefix
        text_length = len(self.lineEdit().text())
        
        self.lineEdit().setCursorPosition(text_length)
        

    def mousePressEvent(self, event):
        # Ensure the cursor is always set right after the prefix on mouse click
        super().mousePressEvent(event)
        text_length = len(self.lineEdit().text())
        self.lineEdit().setCursorPosition(text_length)
    
        
    
        

        
class CustomTreeView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
    def drawRow(self, painter, option, index):
        QTreeView.drawRow(self, painter, option, index)
        painter.setPen(Qt.lightGray)
        y = option.rect.y()
        bottom = option.rect.bottom()
    #saving is mandatory to keep alignment through out the row painting
        painter.save()
        painter.translate(self.visualRect(self.model().index(0, 0)).x() - self.indentation() - .5, -.5)
        for sectionId in range(self.header().count() -1):
            painter.translate(self.header().sectionSize(sectionId), 0)
            painter.drawLine(0, y, 0, y + option.rect.height())
        painter.restore()

        painter.drawLine(0, bottom, option.rect.width(), bottom)



    
        



    



   
        

       