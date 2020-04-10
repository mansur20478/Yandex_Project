import sys
import requests
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from io import BytesIO

from scripts import *


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_gui.ui', self)

        self.my_coord = [0, 0]
        self.spn = 0.005
        self.spn_step = 0.0005
        self.coord_step = 0.0001
        self.map_opt = "map"
        self.photo_path = {
            "sat": "map.jpg",
            "sat,skl": "map.jpg",
            "map": "map.png"
        }
        self.add_postcode = 0
        self.to_search = {
            'coord': "",
            'address': "",
            "postcode": ""
        }

        self.to_map_act.triggered.connect(self.change_to_map)
        self.to_sat_act.triggered.connect(self.change_to_sat)
        self.to_satskl_act.triggered.connect(self.change_to_satskl)
        self.to_search_act.triggered.connect(self.change_to_search)
        self.to_postcode_act.triggered.connect(self.change_postcode)
        self.to_clear_s_act.triggered.connect(self.change_erase)

        self.to_search = get_info("Red square")
        self.my_coord = list(map(float, str.split(self.to_search['coord'], ",")))
        self.update_photo()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            if self.spn + self.spn_step <= 10:
                self.spn += self.spn_step
                self.update_photo()
        if event.key() == Qt.Key_PageDown:
            if self.spn - self.spn_step >= 0.0005:
                self.spn -= self.spn_step
                self.update_photo()
        if event.key() == Qt.Key_Right:
            self.my_coord[0] += self.coord_step
            self.update_photo()
        if event.key() == Qt.Key_Left:
            self.my_coord[0] -= self.coord_step
            self.update_photo()
        if event.key() == Qt.Key_Up:
            self.my_coord[1] += self.coord_step
            self.update_photo()
        if event.key() == Qt.Key_Down:
            self.my_coord[1] -= self.coord_step
            self.update_photo()

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                width = self.frameGeometry().width()
                height = self.frameGeometry().height()
                x, y = event.x(), event.y()

                x1 = self.my_coord[0] + (x - width / 2) * (self.spn * 2 / width)
                y1 = self.my_coord[1] - (y - height / 2) * (self.spn * 2 / height)

                to_search = get_info(str(x1) + "," + str(y1))
                if to_search['coord'] != "":
                    self.to_search['address'] = to_search['address']
                    try:
                        self.to_search['postcode'] = to_search['postcode']
                    except BaseException as exc:
                        self.to_search['postcode'] = "-"
                    self.update_ss()
                    self.search_line.resize(self.search_line.sizeHint())

            if event.button() == Qt.RightButton:
                width = self.frameGeometry().width()
                height = self.frameGeometry().height()
                x, y = event.x(), event.y()

                x = self.my_coord[0] + (x - width / 2) * (self.spn * 2 / width)
                y = self.my_coord[1] - (y - height / 2) * (self.spn * 2 / height)

                dad = get_search(str(x) + "," + str(y), "организация")
                for daddy in dad:
                    x1, y1 = daddy['geometry']['coordinates']
                    # print(daddy)
                    dist = lonlat_distance((x, y), (x1, y1))
                    if dist <= 50:
                        self.to_search['address'] = daddy['properties']['name']
                        self.to_search['postcode'] = "-"
                        self.update_ss()
                        break

    def change_to_map(self):
        self.map_opt = "map"
        self.update_photo()

    def change_to_sat(self):
        self.map_opt = "sat"
        self.update_photo()

    def change_to_satskl(self):
        self.map_opt = "sat,skl"
        self.update_photo()

    def change_postcode(self):
        self.add_postcode ^= 1
        self.update_photo()

    def change_erase(self):
        self.to_search = {
            'coord': "",
            'address': "",
            "postcode": ""
        }
        self.search_line.setText("")
        self.update_photo()

    def change_to_search(self):
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.resize(200, 100)
        dialog.setWindowTitle("Поисковик")
        dialog.setLabelText("Что искать:")
        dialog.setOkButtonText("Искать")
        dialog.setCancelButtonText("Отмена")

        status = dialog.exec_()
        if status == 1:
            to_search = dialog.textValue()

            self.to_search = get_info(to_search)
            self.my_coord = list(map(float, str.split(self.to_search['coord'], ",")))
            self.update_photo()

    def update_ss(self):
        if self.add_postcode:
            self.search_line.setText(self.to_search['address'] + " Индекс: " + self.to_search['postcode'])
        else:
            self.search_line.setText(self.to_search['address'])
        self.search_line.resize(self.search_line.sizeHint())

    def update_photo(self):
        map_params = {
            'll': str(self.my_coord[0]) + "," + str(self.my_coord[1]),
            'spn': str(self.spn) + "," + str(self.spn),
            'l': self.map_opt
        }
        if self.to_search['coord'] != "":
            map_params['pt'] = self.to_search['coord']
            self.update_ss()
        take_photo(self.photo_path[self.map_opt], map_params)
        self.photo_map.setPixmap(QPixmap(self.photo_path[self.map_opt]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
