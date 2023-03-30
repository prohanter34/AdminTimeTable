import psycopg2
import sys
import re
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                         QTableWidgetItem, QPushButton, QMessageBox)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.setWindowTitle("Shedule")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_shedule_tab()
        self._create_teachers_tab()
        self._create_subjects_tab()

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="raspisanie1",
                                     user="postgres",
                                     password="pretki23",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def _create_shedule_tab(self):
        self.shedule_tab = QWidget()

        self.tabs.addTab(self.shedule_tab, "Shedule")
        #
        self.shedule_tab.vbox = QVBoxLayout(self.shedule_tab)

        self.tabs_1 = QTabWidget(self.shedule_tab)
        self.shedule_tab.vbox.addWidget(self.tabs_1)

        self.arr_table = []

        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        counter = 0
        for i in days_of_week:
            counter += 1
            self.day_tab = QWidget()

            self.tabs_1.addTab(self.day_tab, i)
            #
            self.monday_gbox = QGroupBox(i)
            self.svbox = QVBoxLayout(self.day_tab)
            self.shbox1 = QHBoxLayout(self.day_tab)
            self.shbox2 = QHBoxLayout(self.day_tab)

            self.svbox.addLayout(self.shbox1)
            self.svbox.addLayout(self.shbox2)

            self.shbox1.addWidget(self.monday_gbox)

            self._create_monday_table(counter)

            self.update_shedule_button = QPushButton("Update")
            self.shbox2.addWidget(self.update_shedule_button)
            self.update_shedule_button.clicked.connect(lambda ch, num=counter: self._update_shedule(num))

            self.shedule_tab.setLayout(self.svbox)

    def _create_teachers_tab(self):
        self.teachers_tab = QWidget()
        self.tabs.addTab(self.teachers_tab, "Teachers")

        self.monday_gbox = QGroupBox("Teachers")

        self.svbox = QVBoxLayout(self.teachers_tab)
        self.shbox1 = QHBoxLayout(self.teachers_tab)
        self.shbox2 = QHBoxLayout(self.teachers_tab)

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.monday_gbox)

        self._create_teachers_table()

        self.update_shedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_shedule_button)
        self.update_shedule_button.clicked.connect(self._update_teachers)

        self.teachers_tab.setLayout(self.svbox)

    def _create_teachers_table(self):
        self.teachers_table = QTableWidget()

        self.teachers_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.teachers_table.setColumnCount(5)
        self.teachers_table.setHorizontalHeaderLabels(["ID", "Name", "Subject", "", ""])

        self._set_teachers_tab()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.teachers_table)
        self.monday_gbox.setLayout(self.mvbox)

    def _set_teachers_tab(self):


        self.cursor.execute("SELECT * FROM teachers JOIN subjects ON teachers.subject_name = subjects.id;")

        records = list(self.cursor.fetchall())

        self.teachers_table.setRowCount(0)
        self.teachers_table.setRowCount(len(records) + 1)

        addButton = QPushButton("Add")

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            dellButton = QPushButton("Delete")

            self.TabItem = QTableWidgetItem(str(r[0]))
            self.TabItem.setFlags(QtCore.Qt.ItemIsEditable)

            self.teachers_table.setItem(i, 0, self.TabItem)
            self.teachers_table.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.teachers_table.setItem(i, 2, QTableWidgetItem(str(r[4])))

            self.teachers_table.setCellWidget(i, 3, joinButton)
            self.teachers_table.setCellWidget(i, 4, dellButton)

            joinButton.clicked.connect(lambda ch, num=i: self._join_teacher(num))
            dellButton.clicked.connect(lambda ch, num=i: self._delete_teachers(num))


        self.teachers_table.setCellWidget(len(records), 3, addButton)
        addButton.clicked.connect(lambda ch, num=len(records): self._add_teacher(num))

        self.teachers_table.resizeRowsToContents()

    def _add_teacher(self, rowNum):

        row = list()
        for i in range(self.teachers_table.columnCount()):
            try:
                row.append(self.teachers_table.item(rowNum, i).text())
            except:
                row.append(None)

        if row[2] != None:
            self.cursor.execute("SELECT id FROM subjects WHERE subject_name = '{}'".format(row[2]))
            records = self.cursor.fetchall()
            if records != [] and row[1] != None:
                self.cursor.execute(
                    "INSERT INTO teachers (full_name, subject_name) VALUES ('{}', {});".format(row[1], records[0][0]))
                self.conn.commit()
            elif row[1] == None:
                QMessageBox.about(self, "Error", "Заполните все поля")
            elif records == []:
                QMessageBox.about(self, "Error", "Такого предмета не существует")
        else:
            QMessageBox.about(self, "Error", "Заполните все поля")



        self._update_teachers()

    def _delete_teachers(self, rowNum):

        row = list()
        for i in range(self.teachers_table.columnCount()):
            try:
                row.append(self.teachers_table.item(rowNum, i).text())
            except:
                row.append(None)
        self.cursor.execute("DELETE FROM teachers WHERE id = {};".format(row[0]))
        self.conn.commit()
        self._update_teachers()

    def _join_teacher(self, rowNum):

        row = list()
        for i in range(self.teachers_table.columnCount()):
            try:
                row.append(self.teachers_table.item(rowNum, i).text())
            except:
                row.append(None)

        try:

            self.cursor.execute("UPDATE teachers SET full_name = '{}' WHERE id = {};".format(row[1], row[0]))
            self.conn.commit()
            self.cursor.execute("SELECT subject_name FROM subjects WHERE subject_name = '{}';".format(row[2]))
            records = list(self.cursor.fetchall())

            if records == []:
                QMessageBox.about(self, "Error", "Такого предмета не существует")
            else:
                self.cursor.execute("UPDATE teachers SET subject_name = (SELECT id FROM subjects WHERE subject_name = '{}') WHERE id = {};".format(row[2], row[0]))
                self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "Такого предмета не существует")


    def _create_subjects_tab(self):
        self.subjects_tab = QWidget()
        self.tabs.addTab(self.subjects_tab, "Subjects")

        self.monday_gbox = QGroupBox("Subjects")

        self.svbox = QVBoxLayout(self.subjects_tab)
        self.shbox1 = QHBoxLayout(self.subjects_tab)
        self.shbox2 = QHBoxLayout(self.subjects_tab)

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.monday_gbox)

        self._create_subject_table()

        self.update_shedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_shedule_button)
        self.update_shedule_button.clicked.connect(self._update_subjects)

        self.subjects_tab.setLayout(self.svbox)

    def _create_subject_table(self):

        self.subject_table = QTableWidget()
        self.subject_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.subject_table.setColumnCount(4)
        self.subject_table.setHorizontalHeaderLabels(["Name of subject", "ID", "", ""])

        self._set_subject_tab()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.subject_table)
        self.monday_gbox.setLayout(self.mvbox)

    def _join_subject(self, rowNum):

        row = list()
        for i in range(self.subject_table.columnCount()):
            try:
                row.append(self.subject_table.item(rowNum, i).text())
            except:
                row.append(None)

        try:
            self.cursor.execute("UPDATE subjects SET subject_name = '{}' WHERE id = {};".format(row[0], row[1]))
            self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "Enter all fields")

    def _add_subject(self, rowNum):

        row = list()
        for i in range(self.subject_table.columnCount()):
            try:
                row.append(self.subject_table.item(rowNum, i).text())
            except:
                row.append(None)
        print(row)
        if row[0] != None:
            self.cursor.execute("INSERT INTO subjects (subject_name) VALUES ('{}');".format(row[0]))
            self.conn.commit()
        else:
            QMessageBox.about(self, "Error", "Enter all fields")
        self._set_subject_tab()

    def _delete_subject(self, rowNum):

        row = list()
        for i in range(self.subject_table.columnCount()):
            try:
                row.append(self.subject_table.item(rowNum, i).text())
            except:
                row.append(None)
        print(row)
        self.cursor.execute("DELETE FROM subjects WHERE id = {}".format(row[1]))
        self.conn.commit()
        self._set_subject_tab()

    def _set_subject_tab(self):

        self.cursor.execute(
            "SELECT * FROM subjects")
        records = list(self.cursor.fetchall())
        self.subject_table.setRowCount(0)
        self.subject_table.setRowCount(len(records) + 1)

        addButton = QPushButton("Add")

        for i, r in enumerate(records):
            r = list(r)
            delButton = QPushButton('Delete')
            joinButton = QPushButton("Join")

            self.subject_table.setItem(i, 0, QTableWidgetItem(str(r[1])))

            self.TabItem = QTableWidgetItem(str(r[0]))
            self.TabItem.setFlags(QtCore.Qt.ItemIsEditable)

            self.subject_table.setItem(i, 1, self.TabItem)

            self.subject_table.setCellWidget(i, 2, joinButton)
            self.subject_table.setCellWidget(i, 3, delButton)

            joinButton.clicked.connect(lambda ch, num=i: self._join_subject(num))
            delButton.clicked.connect(lambda ch, num=i: self._delete_subject(num))

        self.subject_table.setCellWidget(len(records), 2, addButton)
        addButton.clicked.connect(lambda ch, num=len(records): self._add_subject(num))

        self.subject_table.resizeRowsToContents()

    def _create_monday_table(self, day):
        self.monday_table = QTableWidget()
        self.monday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.monday_table.setColumnCount(8)
        self.monday_table.setHorizontalHeaderLabels(["Subject", "Time", "Room", "Teacher", "Data", "ID", "", ""])

        self._set_monday_table(day)

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.monday_table)
        self.monday_gbox.setLayout(self.mvbox)
        self.arr_table.append(self.monday_table)

    def _set_monday_table(self, day):

        self.cursor.execute("SELECT * FROM timetable JOIN subjects on timetable.subject_name = subjects.id JOIN teachers ON teachers.id = timetable.teacher WHERE extract(week from day)=(SELECT EXTRACT (WEEK FROM NOW())) AND extract(dow from day)={} ORDER BY start_time;".format(day))
        records = list(self.cursor.fetchall())

        self.monday_table.setRowCount(len(records) + 1)

        addButton = QPushButton("Add")

        for i, r in enumerate(records):
            r = list(r)
            joinButton = QPushButton("Join")
            delButton = QPushButton("Delete")

            self.monday_table.setItem(i, 0, QTableWidgetItem(str(r[7])))
            self.monday_table.setItem(i, 1, QTableWidgetItem(str(r[4])[0:5]))
            self.monday_table.setItem(i, 2, QTableWidgetItem(str(r[3])))
            self.monday_table.setItem(i, 3, QTableWidgetItem(str(r[9])))
            self.monday_table.setItem(i, 4, QTableWidgetItem(str(r[1])))

            self.TabItem = QTableWidgetItem(str(r[0]))
            self.TabItem.setFlags(QtCore.Qt.ItemIsEditable)

            self.monday_table.setItem(i, 5, self.TabItem)

            self.monday_table.setCellWidget(i, 6, joinButton)
            self.monday_table.setCellWidget(i, 7, delButton)

            delButton.clicked.connect(lambda ch, num=[i, day - 1]: self._delete_day_timetable(num))
            joinButton.clicked.connect(lambda ch, num=[i, day - 1]: self._change_day_from_table(num))

        self.monday_table.setCellWidget(len(records), 6, addButton)
        addButton.clicked.connect(lambda ch, num=[len(records), day-1]: self._add_day_timetable(num))

        self.monday_table.resizeRowsToContents()

    def _add_day_timetable(self, rowNum):
        row = list()

        for i in range(self.arr_table[rowNum[1]].columnCount()):
            try:
                row.append(self.arr_table[rowNum[1]].item(rowNum[0], i).text())
            except:
                row.append(None)
        print(row)

        if row[0] == None or row[1] == None or row[2] == None or row[3] == None or row[4] == None:
            QMessageBox.about(self, "Error", "Заполните все поля")
        else:
            self.cursor.execute("SELECT id FROM subjects WHERE subject_name = '{}'".format(row[0]))
            records = list(self.cursor.fetchall())
            print(records)
            if records == []:
                QMessageBox.about(self, "Error", "Такого предмета не существует")
            else:
                subject = records[0][0]
                self.cursor.execute("SELECT id FROM teachers WHERE full_name = '{}'".format(row[3]))
                records = self.cursor.fetchall()
                if records == []:
                    QMessageBox.about(self, "Error", "Такого учителя не существует")
                else:
                    teacher = records[0][0]
                    if not re.match("^\d\d\d\d\-\d\d\-\d\d$", row[4]):
                        QMessageBox.about(self, "Error", "Введите дату в правильном формате")
                    else:
                        if not re.match("^\d\d:\d\d$", row[1]):
                            QMessageBox.about(self, "Error", "Введите время в правильном формате")
                        else:
                            try:
                                int(row[2])
                                self.cursor.execute("INSERT INTO timetable (day, subject_name, room_numb, start_time, teacher) VALUES ('{}', {}, {}, '{}', {});"
                                                    .format(row[4], subject, row[2], row[1], teacher))
                                self.conn.commit()
                            except:
                                QMessageBox.about(self, "Error", "Номер кабинета должен быть числом")

        self._update_monday_table(rowNum[1])

    def _delete_day_timetable(self, rowNum):

        row = list()

        for i in range(self.arr_table[rowNum[1]].columnCount()):
            try:
                row.append(self.arr_table[rowNum[1]].item(rowNum[0], i).text())
            except:
                row.append(None)
        self.cursor.execute("DELETE FROM timetable WHERE id = {}".format(row[5]))
        self.conn.commit()
        self._update_monday_table(row[0])

    def _update_monday_table(self, day):
        for j in range(0, 6):

            self.cursor.execute("SELECT * FROM timetable JOIN subjects on timetable.subject_name = subjects.id JOIN teachers ON teachers.id = timetable.teacher WHERE extract(week from day)=(SELECT EXTRACT (WEEK FROM NOW())) AND extract(dow from day)={} ORDER BY start_time;".format(j+1))
            records = list(self.cursor.fetchall())

            self.arr_table[j].setRowCount(0)
            self.arr_table[j].setRowCount(len(records) + 1)

            addButton = QPushButton("Add")

            for i, r in enumerate(records):
                r = list(r)
                joinButton = QPushButton("Join")
                delButton = QPushButton("Delete")

                self.arr_table[j].setItem(i, 0, QTableWidgetItem(str(r[7])))
                self.arr_table[j].setItem(i, 1, QTableWidgetItem(str(r[4])[0:5]))
                self.arr_table[j].setItem(i, 2, QTableWidgetItem(str(r[3])))
                self.arr_table[j].setItem(i, 3, QTableWidgetItem(str(r[9])))
                self.arr_table[j].setItem(i, 4, QTableWidgetItem(str(r[1])))

                self.TabItem = QTableWidgetItem(str(r[0]))
                self.TabItem.setFlags(QtCore.Qt.ItemIsEditable)

                self.arr_table[j].setItem(i, 5, self.TabItem)

                self.arr_table[j].setCellWidget(i, 6, joinButton)
                self.arr_table[j].setCellWidget(i, 7, delButton)

                joinButton.clicked.connect(lambda ch, num=[i, j], : self._change_day_from_table(num))
                delButton.clicked.connect(lambda ch, num=[i, j], : self._delete_day_timetable(num))


            self.arr_table[j].setCellWidget(len(records), 6, addButton)
            addButton.clicked.connect(lambda ch, num=[len(records), j], : self._add_day_timetable(num))
            self.arr_table[j].resizeRowsToContents()


    def _change_day_from_table(self, rowNum):
        row = list()

        for i in range(self.arr_table[rowNum[1]].columnCount()):
            try:
                row.append(self.arr_table[rowNum[1]].item(rowNum[0], i).text())
            except:
                row.append(None)
        print(row)

        try:
            i = int(row[2])
            j = int(row[5])
            self.cursor.execute("UPDATE timetable SET room_numb = {} WHERE id = {}".format(row[2], row[5]))
            self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "Введите число")

        if re.match("^\d\d\d\d\-\d\d\-\d\d$", row[4]):
            self.cursor.execute("UPDATE timetable SET day = '{}' WHERE id = {}".format(row[4], row[5]))
            self.conn.commit()
        else:
            QMessageBox.about(self, "Error", "Введён неправельный формат даты")

        if re.match("^\d\d:\d\d$", row[1]):
            self.cursor.execute("UPDATE timetable SET start_time = '{}' WHERE id = {}".format(row[1], row[5]))
            self.conn.commit()
        else:
            QMessageBox.about(self, "Error", "Введён неправельный формат времени")

        self.cursor.execute("SELECT subject_name FROM subjects WHERE subject_name = '{}';".format(row[0]))
        records = list(self.cursor.fetchall())
        print(records)
        if records == []:
            QMessageBox.about(self, "Error", "Такого предмета не существует")
        else:
            self.cursor.execute(
                "UPDATE timetable SET subject_name = (SELECT id FROM subjects WHERE subject_name = '{}') WHERE id = {};".format(
                    row[0], row[5]))
            self.conn.commit()

        self.cursor.execute("SELECT full_name FROM teachers WHERE full_name = '{}'".format(row[3]))
        records = list(self.cursor.fetchall())
        if records == []:
            QMessageBox.about(self, "Error", "Такого учителя не существует")
        else:
            self.cursor.execute("UPDATE timetable SET teacher = (SELECT id FROM teachers WHERE full_name = '{}') WHERE id = {};".format(row[3], row[5]))


    def _update_shedule(self, i):
        self._update_monday_table(i)

    def _update_teachers(self):
        self._set_teachers_tab()

    def _update_subjects(self):
        self._set_subject_tab()


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())