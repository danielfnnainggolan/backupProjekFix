from PyQt5.QtCore import QSortFilterProxyModel

class CustomProxyModel(QSortFilterProxyModel):
    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return sourceColumn == 1