from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from tela import *
import sys
from operacoes_db import *
from datetime import *
import sqlite3
from time import sleep
import sys

sistema = sys.platform
if sistema == 'linux':
    operacoes = Operacoes('DB/dbase.db')
    foto = 'img/tela.jpg'
else:
    operacoes = Operacoes('DB\\dbase.db')
    foto = 'img\\tela.jpg'


class Acesso:

    def __init__(self, arquivo):
        self.conn = sqlite3.connect(arquivo)
        self.cursor = self.conn.cursor()

    def buscaOperador(self, login):
        try:
            itens = []
            sql = "SELECT * FROM usuarios where login=?"
            self.cursor.execute(sql, (login,))
            contador = 0
            for linha in self.cursor.fetchall():
                contador += 1
                itens.append(linha)
            return itens[0][1], itens[0][2], itens[0][3]
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    sistema = sys.platform
    if sistema == 'linux':
        acesso = Acesso('DB/dbase.db')
        foto = 'img/tela.jpg'
    else:
        acesso = Acesso('DB\\dbase.db')
        foto = 'img\\tela.jpg'

    print(acesso.entraOperador('21220'))
