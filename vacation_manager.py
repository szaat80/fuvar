from PySide6.QtWidgets import QLabel, QMessageBox
from PySide6.QtCore import QDate
import sqlite3

class VacationManager:
    def __init__(self, parent=None):
        self.parent = parent
        self.conn = sqlite3.connect('fuvarok.db')
        self.setupDatabase()
        
    def setupDatabase(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vacation_allowance (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                total_days INTEGER,
                used_days INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def updateVacationDisplay(self):
        try:
            cursor = self.conn.cursor()
            current_year = QDate.currentDate().year()
            
            cursor.execute("""
                SELECT total_days, used_days 
                FROM vacation_allowance 
                WHERE year = ?
            """, (current_year,))
            
            result = cursor.fetchone()
            if result:
                total_days, used_days = result
                self.parent.vacation_label.setText(f"Szabadság: {used_days}/{total_days}")
            else:
                cursor.execute("""
                    INSERT INTO vacation_allowance (year, total_days, used_days)
                    VALUES (?, 29, 0)
                """, (current_year,))
                self.conn.commit()
                self.parent.vacation_label.setText("Szabadság: 0/29")
                
        except Exception as e:
            print(f"Hiba a szabadság megjelenítésekor: {str(e)}")

    def updateVacationDays(self):
        try:
            current_year = QDate.currentDate().year()
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT total_days, used_days 
                FROM vacation_allowance 
                WHERE year = ?
            """, (current_year,))
            
            result = cursor.fetchone()
            if result:
                total_days, used_days = result
                used_days += 1
                
                cursor.execute("""
                    UPDATE vacation_allowance 
                    SET used_days = ? 
                    WHERE year = ?
                """, (used_days, current_year))
                
                self.conn.commit()
                self.parent.vacation_label.setText(f"Szabadság: {used_days}/{total_days}")
            
        except Exception as e:
            print(f"Hiba a szabadság frissítésekor: {str(e)}")
            QMessageBox.warning(self.parent, "Hiba", f"Hiba a szabadság frissítésekor: {str(e)}")

    def getVacationData(self, year=None):
        if year is None:
            year = QDate.currentDate().year()
            
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT total_days, used_days 
            FROM vacation_allowance 
            WHERE year = ?
        """, (year,))
        
        result = cursor.fetchone()
        if result:
            return {"total": result[0], "used": result[1]}
        return {"total": 29, "used": 0}

    def setVacationDays(self, year, total_days):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO vacation_allowance (year, total_days, used_days)
                VALUES (?, ?, COALESCE((SELECT used_days FROM vacation_allowance WHERE year = ?), 0))
            """, (year, total_days, year))
            
            self.conn.commit()
            self.updateVacationDisplay()
            return True
            
        except Exception as e:
            print(f"Hiba a szabadság keret beállításakor: {str(e)}")
            return False

    def resetVacationDays(self, year):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE vacation_allowance 
                SET used_days = 0
                WHERE year = ?
            """, (year,))
            
            self.conn.commit()
            self.updateVacationDisplay()
            return True
            
        except Exception as e:
            print(f"Hiba a szabadság nullázásakor: {str(e)}")
            return False