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

        self.frame_subtotal.hide()

        self.lbl_total.setText('R$ 0.00')
        self.lbl_item.setText('')
        # verifica se existe cupom aberto
        self.verificaCupomAberto()

        # entrada de ean na passagem de compra
        self.txt_ean.setFocus()
        self.txt_ean.returnPressed.connect(self.adicionaItem)

        # menu de acoes
        self.actionFinalizaCupom.triggered.connect(self.abreSubtotal)

        # acoes do subtotal
        self.rb_dinheiro.toggled.connect(lambda: self.calculaTroco("dinheiro"))
        self.rb_debito.toggled.connect(lambda: self.calculaTroco("debito"))
        self.rb_credito.toggled.connect(lambda: self.calculaTroco("credito"))
        self.rb_pix.toggled.connect(lambda: self.calculaTroco("pix"))
        self.ed_valorPago.textEdited.connect(lambda: self.exibeTroco())

    def adicionaItem(self):
        ean = self.txt_ean.text().replace('x', 'X').split('X')
        if len(ean) > 1:
            qtd, ean = ean
        else:
            qtd, ean = 1, ean[0]

        retorno = operacoes.buscarProduto(ean)
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
                operacoes.adicionaItem(retorno[1], retorno[2], retorno[5])
                self.lst_itens.scrollToBottom()
                self.txt_ean.setText('')
        else:
            QMessageBox.warning(
                self, 'Aviso', f'Produto nao encontrado')
            self.txt_ean.setText('')

    def verificaCupomAberto(self):
        # total = self.lbl_total.text().replace('R$ ', '')
        total = float(0)
        retorno = operacoes.listar_tmp()
        for i in retorno:
            total += float(i[2])
            self.lst_itens.addItem(
                f'{i[0]} {i[1]} - 1x{i[2]}')

        total = "{:.2f}".format(total)
        self.lbl_total.setText(f'R$ {total}')

    def abreSubtotal(self):
        self.frame_subtotal.show()
        self.frame_subtotal.move(50, 50)
        totalCompra = self.lbl_total.text()
        self.lb_total.setText(totalCompra)

    def calculaTroco(self, tipo):
        totalCompra = self.lbl_total.text()
        self.ed_valorPago.setText(totalCompra)
        radioButton = self.sender()

        if radioButton.isChecked():
            if tipo == 'debito' or tipo == 'credito' or tipo == 'pix':
                self.ed_valorPago.setEnabled(False)
            elif tipo == 'dinheiro':
                self.ed_valorPago.setEnabled(True)
                self.ed_valorPago.setFocus()

    def exibeTroco(self):
        try:
            total = float(self.lb_total.text().replace('R$ ', ''))
            pago = float(self.ed_valorPago.text().replace('R$ ', ''))
            troco = float(pago)-float(total)
            self.lb_troco.setText(f'R$ {troco}')
        except:
            pass


qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
