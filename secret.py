from PyQt5.QtWidgets import QApplication

class MyApp(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_id = None
        self.username = None

