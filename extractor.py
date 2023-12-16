import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class LinkExtractor(QThread):
    progress = pyqtSignal(int)

    def __init__(self, pdf_path, separator):
        QThread.__init__(self)
        self.pdf_path = pdf_path
        self.separator = separator

    def run(self):
        doc = fitz.open(self.pdf_path)
        links = []
        for i in range(len(doc)):
            links.extend(doc[i].get_links())
            self.progress.emit((i + 1) * 100 // len(doc))
        file_links = [link['uri'] for link in links if '/file/' in link['uri']]
        folder_links = [link['uri'] for link in links if '/folders/' in link['uri']]
        with open('file_links.txt', 'w') as f:
            f.write(self.separator.join(file_links))
        with open('folder_links.txt', 'w') as f:
            f.write(self.separator.join(folder_links))

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Link Extractor')
        self.setGeometry(100, 100, 200, 100)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.btn_select = QPushButton('Select PDF', self)
        self.btn_select.clicked.connect(self.select_pdf)
        layout.addWidget(self.btn_select)

        self.btn_start = QPushButton('Start', self)
        self.btn_start.clicked.connect(self.start_extraction)
        self.btn_start.setEnabled(False)
        layout.addWidget(self.btn_start)

        self.progress = QProgressBar(self)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setStyleSheet("QProgressBar::chunk { background-color: blue; }")
        layout.addWidget(self.progress)

    def select_pdf(self):
        self.pdf_path, _ = QFileDialog.getOpenFileName(self, 'Select PDF', '', 'PDF Files (*.pdf)')
        if self.pdf_path:
            self.separator, ok = QInputDialog.getItem(self, 'Select Separator', 'Separator:', [',', ' ', '\\n', 'Custom'], 0, False)
            if ok and self.separator == 'Custom':
                self.separator, ok = QInputDialog.getText(self, 'Custom Separator', 'Enter custom separator:')
            if ok:
                self.btn_start.setEnabled(True)

    def start_extraction(self):
        self.extractor = LinkExtractor(self.pdf_path, self.separator)
        self.extractor.progress.connect(self.progress.setValue)
        self.extractor.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
