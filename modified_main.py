from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QLineEdit, QDateEdit, QTimeEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QApplication, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QTime, QTimer
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
import sys
import sqlite3
import os
from datetime import datetime

from work_hours_manager import WorkHoursManager
from delivery_manager import DeliveryManager 
from vacation_manager import VacationManager
from database_manager import DatabaseManager
from driver_file_manager import DriverFileManager
from menu_manager import MenuBar
from ui_manager import UIManager

class FuvarAdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initManagers()
        self.initUI()
        self.setupConnections()

    def initManagers(self):
        self.conn = sqlite3.connect('fuvarok.db')
        self.file_manager = DriverFileManager()
        self.work_hours_manager = WorkHoursManager(self)
        self.delivery_manager = DeliveryManager(self)
        self.vacation_manager = VacationManager(self)
        self.ui_manager = UIManager(self)
        self.database_manager = DatabaseManager(self)
        
        self.file_manager.create_driver_folders()

    def initUI(self):
        self.setWindowTitle("Fuvar Adminisztráció")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # Initialize UI components
        self.initializeComponents()
        
        # Create frames
        top_frame = self.ui_manager.createTopFrame()
        bottom_frame = self.ui_manager.createBottomFrame()
        
        # Set up tables
        self.work_hours_manager.setup_work_table(self.work_table)
        self.delivery_manager.setup_delivery_table(self.delivery_table)
        
        # Add frames to main layout
        main_layout.addWidget(top_frame)
        main_layout.addWidget(bottom_frame)
        
        main_widget.setLayout(main_layout)
        self.setMenuBar(MenuBar(self))
        
        # Load initial data
        self.loadInitialData()
        self.showMaximized()

    def initializeComponents(self):
        self.driver_combo = QComboBox()
        self.vehicle_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.start_time = QTimeEdit()
        self.end_time = QTimeEdit()
        self.type_combo = QComboBox()
        self.km_combo = QComboBox()
        self.factory_combo = QComboBox()
        self.address_input = QLineEdit()
        self.delivery_input = QLineEdit()
        self.m3_input = QLineEdit()
        self.m3_sum = QLabel("(0)")
        self.vacation_label = QLabel("Szabadság: 0/0")
        self.work_table = QTableWidget()
        self.delivery_table = QTableWidget()

        # Set up component properties
        self.setupComponentProperties()

    def setupComponentProperties(self):
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        self.type_combo.addItems([
            "Sima munkanap", 
            "Műhely nap", 
            "Szabadság", 
            "Betegszabadság (TP)"
        ])
        
        self.km_combo.addItems([
            f"Övezet {i}-{i+5}" for i in range(0, 50, 5)
        ])

    def setupConnections(self):
        # Connect signals to slots
        self.m3_input.returnPressed.connect(self.delivery_manager.handleM3Input)
        self.type_combo.currentTextChanged.connect(self.onWorkTypeChanged)

    def loadInitialData(self):
        self.loadDrivers()
        self.loadVehicles()
        self.loadFactories()
        self.loadWorkHours()
        self.vacation_manager.updateVacationDisplay()

    def loadDrivers(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM drivers ORDER BY name")
            drivers = cursor.fetchall()
            self.driver_combo.clear()
            self.driver_combo.addItems([driver[0] for driver in drivers])
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba a sofőrök betöltésekor: {str(e)}")

    def loadVehicles(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT plate_number FROM vehicles ORDER BY plate_number")
            vehicles = cursor.fetchall()
            self.vehicle_combo.clear()
            self.vehicle_combo.addItems([vehicle[0] for vehicle in vehicles])
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba a járművek betöltésekor: {str(e)}")

    def loadFactories(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT nev FROM factories ORDER BY nev")
            factories = cursor.fetchall()
            self.factory_combo.clear()
            self.factory_combo.addItems([factory[0] for factory in factories])
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba a gyárak betöltésekor: {str(e)}")

    def loadWorkHours(self):
        if os.path.exists('work_hours.json'):
            self.work_hours_manager.loadFromExcel()

    def onWorkTypeChanged(self, work_type):
        if work_type == "Szabadság":
            self.vacation_manager.updateVacationDays()

    def saveWorkHoursAndExport(self):
        current_driver = self.driver_combo.currentText()
        if not current_driver:
            QMessageBox.warning(self, "Hiba", "Válasszon sofőrt!")
            return
        
        self.work_hours_manager.saveWorkHours()
        self.work_hours_manager.saveWorkHoursToExcel()

    def saveDeliveryAndExport(self):
        current_driver = self.driver_combo.currentText()
        if not current_driver:
            QMessageBox.warning(self, "Hiba", "Válasszon sofőrt!")
            return
            
        self.delivery_manager.saveDeliveryData()
        self.delivery_manager.saveDeliveryToExcel()
        self.file_manager.organize_delivery_data(current_driver=current_driver)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FuvarAdminApp()
    window.show()
    sys.exit(app.exec())