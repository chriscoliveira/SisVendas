# C:\Users\Christian\AppData\Roaming\Python\Python310\Scripts\pyuic5.exe -x .\tela.ui -o .\tela.py

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
import os
from tela import *
import sys
from operacoes_db import *
operacoes = Operacoes('DB\\dbase.db')


class Novo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)

        # self.lst_itens.setAutoScroll(True)

        self.lbl_total.setText('R$ 0.00')
        self.txt_ean.setFocus()
        self.txt_ean.returnPressed.connect(self.adicionaItem)

    def adicionaItem(self):
        ean = self.txt_ean.text().replace('x', 'X').split('X')
        if len(ean) > 1:
            qtd, ean = ean
        else:
            qtd, ean = 1, ean[0]

        retorno = operacoes.buscar(ean)
        print(f'{retorno=}')

        if retorno[0] == 1:
            self.lbl_item.setText(
                f' {qtd}x {retorno[2]}')
            for i in range(int(qtd)):
                total = self.lbl_total.text().replace('R$ ', '')
                total = float(total)+float(retorno[5])
                self.lbl_total.setText(f'R$ {total}')

                self.lst_itens.addItem(
                    f'{retorno[1]} {retorno[2]} - 1x{retorno[5]}')
                self.lst_itens.scrollToBottom()
                self.txt_ean.setText('')
        else:
            QMessageBox.warning(
                self, 'Aviso', f'Produto nao encontrado')
            self.txt_ean.setText('')


qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
