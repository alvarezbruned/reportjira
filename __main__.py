import json
from os.path import expanduser

import subprocess
import requests
import sys
import os
import threading
import urllib
import logging
# import logging.handlers
import yaml
from datetime import datetime

from PyQt5.QtCore import QSize as QSize
from PyQt5.QtGui import QColor as QColor
from PyQt5.QtGui import QIcon as QIcon
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QApplication, QGridLayout, QComboBox, \
        QMessageBox, QLCDNumber, QHBoxLayout, QFileDialog, QLabel, QCheckBox

from urllib import request, parse
import time
from easysettings import EasySettings

inicio_de_tiempo = ''
tiempo_final = ''


class ReportJira(QDialog):
    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        self.pathImages = ''
        self.usernameJira = ''
        self.tokenJira = ''
        self.domainJira = ''
        self.logoApp = ''
        self.settings = EasySettings(os.path.abspath(os.path.dirname(__file__)) + '/reportjira-config.conf')
        self.jiraIdInProgress = ''
        self.jiraIdFinished = ''
        self.jiraMessageInProgress = ''
        self.jiraMessageFinished = ''
        self.seconds = 0
        self.pixelsIcon = 60
        self.pathToLog = ''
        QDialog.__init__(self)

        # group_layout = QHBoxLayout()
        self.core_layout = QGridLayout()

        self.basic_and_custom_buttons_layout = QGridLayout()

        self.basic_buttons_layout = QGridLayout()
        self.buttons_custom_layout = QGridLayout()

        # self.settingsLayout = QGridLayout()

        # toggle
        self.basic_and_custom_buttons_layout.addLayout(self.basic_buttons_layout, 0, 0)
        self.mi_toggle = self.toogle_on_off()
        self.basic_and_custom_buttons_layout.addLayout(self.buttons_custom_layout, 0, 1)

        self.core_layout.addLayout(self.basic_and_custom_buttons_layout, 0, 0)

        self.tiketForce = QLineEdit()
        self.tiketForce.setPlaceholderText('Jira ticketID')
        self.tiketComment = QLineEdit()
        self.tiketComment.setPlaceholderText('Worklog Comment')
        self.labelApp = QLabel()
        self.getTiketsButton = QPushButton("Reload tickets")
        self.getTiketsButton.clicked.connect(self.get_tikets)
        self.processTiketsButton = QPushButton("Send backups")
        self.jiraTikets = QComboBox()
        self.jiraTikets.setMaximumWidth(150)
        self.lcd = QLCDNumber()
        self.lcd.setNumDigits(8)
        self.lcd.setMaximumHeight(35)
        self.lcd2 = QLCDNumber()
        self.lcd2.setNumDigits(8)
        self.lcd2.setMaximumHeight(35)

        palette = self.lcd.palette()
        palette.setColor(palette.WindowText, QColor(0, 1, 1))
        palette.setColor(palette.Background, QColor(0, 1, 1))
        palette.setColor(palette.Light, QColor(0, 1, 1))
        palette.setColor(palette.Dark, QColor(0, 1, 1))
        self.lcd.setPalette(palette)
        palette.setColor(palette.Light, QColor(1, 0, 1))
        self.lcd2.setPalette(palette)

        self.tipo=''
        self.tiket = ''
        self.inicio_de_tiempo = time.time()
        self.run_thread = True
        self.type = ''
        self.setLayout(self.core_layout)

        self.jira_ticketButton = QPushButton("jira")
        self.stopButton = QPushButton("Stop")
        self.exitButton = QPushButton("Exit")
        self.settingsButton = QPushButton("Settings")

        self.jira_ticketButton.clicked.connect(self.send_tikets_level_2)
        self.typeStopButton = self.set_type("exit", "")
        self.stopButton.clicked.connect(self.typeStopButton)
        self.settingsButton.clicked.connect(self.settings_section)
        self.exitButton.clicked.connect(self.on_click_cancel_button)
        self.processTiketsButton.clicked.connect(self.process_backup_file_worklogs)

        self.first_section_buttons = [
            self.lcd,
            self.lcd2,
            self.tiketForce,
            self.getTiketsButton,
            self.jiraTikets,
            self.jira_ticketButton,
            self.stopButton,
            self.settingsButton,
            self.exitButton,
            self.processTiketsButton
        ]

        self.set_buttons_max_height()
        self.set_buttons_max_width()
        self.add_basic_buttons_to_layouts()

        self.yamlPath = ''
        if self.settings.get('datapath') != '':
            self.yamlPath = self.settings.get('datapath')
            data_loaded = yaml.load(open(self.yamlPath, 'r'))
            self.pathToLog = data_loaded['pathToLog'] if 'pathToLog' in data_loaded else ''
            self.make_buttons(data_loaded, self.buttons_custom_layout)
            self.get_tikets()
        else:
            self.settings_section()

        self.run()

    def toogle_on_off(self):
        self.col = QColor(0, 0, 0)
        toggleButton = QCheckBox('minimize basic buttons')
        toggleButton.setChecked(True)
        toggleButton.stateChanged.connect(self.on_off_first_section)
        return toggleButton

    def on_off_first_section(self):
        if not self.mi_toggle.isChecked():
            for button in self.first_section_buttons:
                button.setVisible(False)
                self.basic_buttons_layout.update()
        else:
            for button in self.first_section_buttons:
                button.setVisible(True)

    def settings_section(self):
        input_file = QFileDialog.getOpenFileName(None, 'Select a file:', expanduser("pwd"))
        self.yamlPath = input_file[0]
        logging.info(self.yamlPath)
        # Read YAML file
        if self.yamlPath != '':
            self.settings.set('datapath', self.yamlPath)
            self.settings.save()
            data_loaded = yaml.load(open(self.yamlPath, 'r'))
            self.pathToLog = data_loaded['pathToLog'] if 'pathToLog' in data_loaded else ''
            self.make_buttons(data_loaded, self.buttons_custom_layout)
            self.get_tikets()
        else:
            logging.warning('No yaml selected')

    def set_buttons_max_height(self):
        buttonHeight = int(self.pixelsIcon / 3)
        for button in self.first_section_buttons:
            button.setMaximumHeight(buttonHeight)

    def set_buttons_max_width(self):
        buttonWidth = int(self.pixelsIcon * 2)
        for button in self.first_section_buttons:
            button.setFixedWidth(buttonWidth)

    def add_basic_buttons_to_layouts(self):
        self.basic_buttons_layout.addWidget(self.lcd, 0, 0)
        self.basic_buttons_layout.addWidget(self.lcd2, 1, 0)
        self.basic_buttons_layout.addWidget(self.tiketForce, 2, 0)
        self.basic_buttons_layout.addWidget(self.getTiketsButton, 3, 0)
        self.basic_buttons_layout.addWidget(self.jiraTikets, 4, 0)
        self.core_layout.addWidget(self.tiketComment, 1, 0)
        self.core_layout.addWidget(self.labelApp, 2, 0)
        self.core_layout.addWidget(self.mi_toggle, 3, 0)
        self.basic_buttons_layout.addWidget(self.jira_ticketButton, 0, 1)
        self.basic_buttons_layout.addWidget(self.stopButton, 1, 1)
        self.basic_buttons_layout.addWidget(self.settingsButton, 2, 1)
        self.basic_buttons_layout.addWidget(self.exitButton, 3, 1)
        self.basic_buttons_layout.addWidget(self.processTiketsButton, 4, 1)

    def make_buttons(self, data_loaded, layout):
        self.pathImages = data_loaded['pathImages']
        self.pixelsIcon = int(data_loaded['pixelsIcon']) if 'pixelsIcon' in data_loaded else self.pixelsIcon
        self.usernameJira = data_loaded['usernameJira'] if 'usernameJira' in data_loaded else ''
        self.tokenJira = data_loaded['tokenJira'] if 'tokenJira' in data_loaded else ''
        self.domainJira = data_loaded['domainJira'] if 'domainJira' in data_loaded else ''
        self.logoApp = data_loaded['logo'] if 'logo' in data_loaded else None
        if isinstance(self.logoApp, str):
            self.setWindowIcon(QIcon(self.pathImages + self.logoApp))
        for rowData in range(0, len(data_loaded['data'])):
            rowItems = data_loaded['data'][rowData]['row' + str(rowData)]
            for itemRow in range(0, (len(rowItems))):
                items = rowItems[itemRow]
                for keyItem in items.keys():
                    tiketItem = items[keyItem][0] if isinstance(items[keyItem], list) else ''
                    logging.info(items[keyItem])
                    imageFileName = items[keyItem][1] if isinstance(items[keyItem], list) else ''
                    bashScriptFileName = items[keyItem][2] if len(items[keyItem]) > 2 else ''
                    if imageFileName == '':
                        newButton = QPushButton(keyItem)
                    else:
                        newButton = QPushButton()
                        self.add_icon(newButton, imageFileName)
                    self.type = keyItem
                    if keyItem == "none":
                        logging.info("none button")
                    elif keyItem == "exit":
                        newButton.clicked.connect(self.on_click_cancel_button)
                    elif keyItem == "jira_ticket":
                        newButton.clicked.connect(self.send_tikets_level_2)
                    elif keyItem == "stop":
                        typeButton = self.set_type("exit", tiketItem)
                        newButton.clicked.connect(typeButton)
                    elif bashScriptFileName != '':
                        if tiketItem == "CMD ONLY":
                            typeButton = self.set_type_command_only(bashScriptFileName)
                            newButton.clicked.connect(typeButton)
                        else:
                            typeButton = self.set_type_command(keyItem, tiketItem, bashScriptFileName)
                            newButton.clicked.connect(typeButton)
                    else:
                        typeButton = self.set_type(keyItem, tiketItem)
                        newButton.clicked.connect(typeButton)
                    layout.addWidget(newButton, rowData, itemRow)

    def add_icon(self, button, filename):
        button.setIcon(QIcon(self.pathImages + filename))
        button.setIconSize(QSize((self.pixelsIcon + 10), self.pixelsIcon))
        button.setMaximumWidth(self.pixelsIcon+20)

    def _run(self):
        while self.run_thread:
            time.sleep(1)
            self.final_time()

    def run(self):
        threading.Thread(target=self._run).start()

    def on_click_cancel_button(self):
        logging.info('PyQt5 cancel button click')
        self.run_thread=False
        self.close()

    def set_type(self, type, tiket):
        def _function():
            logging.info('click ' + type + ' button')
            self.tipo = type
            if tiket != '':
                self.tiket=tiket
            self.send_tipo_action(tiket, self.tiketComment.text())
            self.tiketComment.setText('')
            self.tiket = ''
        return _function

    def set_type_command_only(self, absolutePath):
        def _function():
            logging.info('execute: ' + absolutePath + ' ' + self.tiketComment.text())
            cmd = subprocess.call(absolutePath + ' ' + self.tiketComment.text(), shell=True)
            self.tiketComment.setText('')
        return _function

    def set_type_command(self, type, tiket, absolutePath):
        def _function():
            logging.info('click ' + type + ' button')
            self.tipo = type
            if tiket != '':
                self.tiket=tiket
            self.send_tipo_action(tiket, self.tiketComment.text())
            self.tiketComment.setText('')
            self.tiket = ''
            logging.info('execute: ' + absolutePath)
            cmd = subprocess.call(absolutePath, shell=True)
        return _function

    def send_stop(self):
        self.set_type('exit', '')

    def send_tikets_level_2(self):
        try:
            self.tipo = 'Tikets_Nivel_2'
            self.tiket = self.tiketForce.text()
            if self.tiket == '':
                arrayTikets = self.jiraTikets.currentText().split('#')
                self.tiket = arrayTikets[0]
            self.send_tipo_action(self.tiket, self.tiketComment.text())
            self.tiket = ''
            self.tiketForce.setText('')
            self.tiketComment.setText('')
        except Exception as e:
            self.popup()

    def get_tikets(self):
        try:
            url = 'https://'+self.domainJira+'/rest/api/2/search?jql=status%20!%3D%20Done%20AND%20assignee%20in%20(' + self.usernameJira.split('@')[0] +')&fields=key,summary'
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            req = requests.request('GET', url, headers=headers, auth=(self.usernameJira, self.tokenJira))
            dataTiketsJir = json.loads(req.text)
            self.jiraTikets.clear()
            for tiket in range(0, len(dataTiketsJir['issues'])):
                ticketId = dataTiketsJir['issues'][tiket]['key']
                titleTicket = dataTiketsJir['issues'][tiket]['fields']['summary']
                self.jiraTikets.addItem(ticketId + '# ' + titleTicket)
            logging.info('assigned tickets have been loaded')
        except Exception as e:
             self.popup_info('some wrong in get tickets info' + str(e))

    def write_backup_file_worklogs(self, file_name, worklog):
        f = open(self.pathImages + file_name, "a")
        f.write("%s" % worklog)

    def write_backup_file_worklogs_by_path(self, fullPath, worklog):
        f = open(fullPath, "a")
        f.write("%s" % worklog + "\n")

    def process_backup_file_worklogs(self):
        with open(self.pathImages + "reportjira-no-connection.txt") as backupFile:
            dataBackupFile = backupFile.read()
            self.truncate_file(self.pathImages + "reportjira-no-connection.txt")
            lines = dataBackupFile.split('|||')
            for worklog in range(0, len(lines)):
                logging.info(lines[worklog])
                if lines[worklog] != '':
                    self.send_worklogs(lines[worklog])

    def truncate_file(self, filePath):
        f = open(filePath, 'r+')
        f.truncate(0)

    def prepare_data_to_send(self, ticket, commentText, totalTime):
        commentText = commentText if commentText != '' else ''
        currentSecond = str(datetime.now().second)
        currentMinute = str(datetime.now().minute)
        currentHour = str(datetime.now().hour)

        currentDay = str(datetime.now().day)
        currentMonth = str(datetime.now().month)
        currentYear = str(datetime.now().year)

        values = '{"comment": "' + commentText + '","started": "' + currentYear + '-' + currentMonth + '-' + currentDay + 'T' + currentHour + ':' + currentMinute + ':' + currentSecond + '.000+0000","timeSpent": "' + totalTime + '"}'
        if self.pathToLog != '':
            timeSplit = totalTime.split("h ")
            timeMinutes = (int(timeSplit[0]) * 60) + int(timeSplit[1][0:-1])
            logging.info('minutes:' + str(timeMinutes))
            self.write_backup_file_worklogs_by_path(self.pathToLog, '{"ticket": "' + ticket + '", "comment": "' + commentText + '","started": "' + currentYear + '-' + currentMonth + '-' + currentDay + 'T' + currentHour + ':' + currentMinute + ':' + currentSecond + '.000+0000","minutesSpent": ' + str(timeMinutes) + '}')
        logging.info(values)
        return ticket + '@||@' + values

    def send_worklogs(self, values):
        try:
            valuesSplited = values.split('@||@')
            if valuesSplited[0] == "CMD ONLY":
                logging.info('ticketID= ' + valuesSplited[0] + ' no sended')
            elif isinstance(valuesSplited, list):
                logging.info('ticketID= ' + valuesSplited[0])
                logging.info('data to send= ' + valuesSplited[1])
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                url = 'https://' + self.domainJira + '/rest/api/2/issue/' + valuesSplited[0] + '/worklog'
                request = requests.request("POST", url, headers=headers, data=valuesSplited[1],
                                           auth=(self.usernameJira, self.tokenJira))
                statuscode = str(request.status_code)
                logging.info('status code ' + statuscode)
                if statuscode == '201':
                    logging.info('reponse OK')
                elif statuscode == '400' and "00h 00m" in valuesSplited[1]:
                    self.popup_info('statuscode 400 - time spent is 00h 00m')
                else:
                    logging.info('statuscode= ' + statuscode)
                    self.popup_info('statuscode= ' + statuscode + ' is saved in backup file')
                    self.write_backup_file_worklogs("reportjira-no-connection.txt", '|||' + values)
            else:
                logging.info('values no data found')
        except Exception as e:
            logging.error(str(e.args))
            self.write_backup_file_worklogs("reportjira-no-connection.txt", '|||' + values)
            logging.info('some wrong - backup data in ' + self.pathImages)

    def send_tipo_action(self, ticket, commentText):
        totalTime = self.final_time_then()
        self.jiraIdInProgress = ticket
        self.jiraMessageInProgress = commentText
        if ticket != '':
            self.labelApp.setText(ticket + ' started')
        if ticket == "CMD ONLY":
            self.labelApp.setText(ticket + ' started no sended')
            logging.info('ticketID= ' + ticket + ' no sended')
        elif self.jiraIdFinished != '':
            self.labelApp.setText(self.jiraIdFinished + ' finished')
            if ticket != '':
                self.labelApp.setText(self.labelApp.text() + ' - ' + ticket + ' started')
            self.send_worklogs(self.prepare_data_to_send(self.jiraIdFinished, commentText, totalTime))
        else:
            logging.info('No ticketId - nothing to send Jira')
        if self.jiraIdFinished == '' and ticket == '':
            self.labelApp.setText('')
        self.jiraIdFinished = self.jiraIdInProgress
        self.jiraMessageFinished = self.jiraMessageInProgress
        self.start_time()

    def start_time(self):
        self.inicio_de_tiempo = time.time()

    def final_time(self):
        time_passed = self.final_time_action()
        self.lcd.display(time_passed)

    def final_time_then(self):
        time_passed = self.final_time_action()
        logging.info(time_passed)
        self.lcd2.display(time_passed)
        return time_passed

    def final_time_action(self):
        self.tiempo_final = time.time()
        tiempo_transcurrido = self.tiempo_final - self.inicio_de_tiempo
        seconds = tiempo_transcurrido
        minutes = seconds / 60
        if minutes == 0:
            hours = 0
        else:
            hours = minutes / 60
        if seconds > 60:
            seconds = (seconds % 60)
        if minutes > 60:
            minutes = (minutes % 60)
        if minutes < 10:
            time_passed = "0%dh 0%dm" % (hours, minutes)
        else:
            time_passed = "0%dh %dm" % (hours, minutes)
        return time_passed

    def popup(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Some is wrong")
        msg.setInformativeText("Connection trouble maybe")
        msg.setWindowTitle("Alert")
        retval = msg.exec_()

    def popup_info(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Message")
        msg.setInformativeText(message)
        msg.setWindowTitle("Alert")
        retval = msg.exec_()

    # def check_path(self, base_url, path_rules, status_code, location):
    #     request = ''
    #     try:
    #         url = base_url + path_rules
    #         request = requests.post(url=url, data=body)
    #         request = requests.get(url, allow_redirects=False)
    #         if (request.status_code == status_code) and (status_code != 301):
    #             logging.info('URL: ' + base_url + path_rules + ' - Expected ' + str(status_code) + ' - Response: ' + str(request.status_code) + ' OK')
    #         elif status_code == 301 and (request.status_code == status_code):
    #             if request.headers['Location'] == location:
    #                 logging.info('URL: ' + base_url + path_rules + ' - Expected ' + str(
    #                     status_code) + ' - Response: ' + str(request.status_code) + ' - Expected location ' + location + ' OK')
    #
    #     except Exception as e:
    #         logging.error('Exception: ' + str(e.args) + 'URL: ' + base_url + path_rules + ' - Expected ' + str(
    #             status_code) + ' - Response: ' + str(request.status_code) + ' - Expected location ' + location + ' FAIL')

app = QApplication(sys.argv)
dialog = ReportJira()
dialog.show()
# fileIn = QFileSystemWatcher()

app.exec_()
