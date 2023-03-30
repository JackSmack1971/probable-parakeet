import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from configparser import ConfigParser
from main import main 

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.config = ConfigParser()
        self.config.read('config.ini') 

    def initUI(self):
        # create input labels and fields
        api_key_label = QLabel('API Key:')
        self.api_key_field = QLineEdit()
        shop_id_label = QLabel('Shop ID:')
        self.shop_id_field = QLineEdit()
        spreadsheet_id_label = QLabel('Spreadsheet ID:')
        self.spreadsheet_id_field = QLineEdit() 

        # create process button and connect to click event
        process_button = QPushButton('Process')
        process_button.clicked.connect(self.process) 

        # create layout for input fields
        input_layout = QVBoxLayout()
        input_layout.addWidget(api_key_label)
        input_layout.addWidget(self.api_key_field)
        input_layout.addWidget(shop_id_label)
        input_layout.addWidget(self.shop_id_field)
        input_layout.addWidget(spreadsheet_id_label)
        input_layout.addWidget(self.spreadsheet_id_field) 

        # create layout for process button
        button_layout = QHBoxLayout()
        button_layout.addWidget(process_button) 

        # create main layout for input fields and process button
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout) 

        # set main layout for the widget
        self.setLayout(main_layout)
        self.setWindowTitle('EtsyInsite') 

    def process(self):
        # validate user input
        api_key = self.api_key_field.text().strip()
        shop_id = self.shop_id_field.text().strip()
        spreadsheet_id = self.spreadsheet_id_field.text().strip()
        if not api_key or not shop_id or not spreadsheet_id:
            QMessageBox.warning(self, 'Error', 'Please enter all required fields.')
            return 

        # update config file
        self.config.set('ETSY', 'API_KEY', api_key)
        self.config.set('ETSY', 'SHOP_ID', shop_id)
        self.config.set('GOOGLE_SHEET', 'SPREADSHEET_ID', spreadsheet_id)         with open('config.ini', 'w') as config_file:             self.config.write(config_file) 

        # process listings data         try:             main(self.config)             QMessageBox.information(self, 'Success', 'Listings data processed successfully.')         except Exception as e:             QMessageBox.critical(self, 'Error', f'Error: {str(e)}') 

if name == 'main':     app = QApplication(sys.argv)     ex = MyApp()     ex.show()     sys.exit(app.exec_())
