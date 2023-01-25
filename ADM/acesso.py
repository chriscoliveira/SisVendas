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
from datetime import date
from datetime import datetime

data_e_hora_atuais = datetime.now()
data_atual = date.today()
data = data_e_hora_atuais.strftime('%d-%m-%Y %H:%M:%S')

sistema = sys.platform
if sistema == 'linux':
    operacoes = Operacoes('../DB/dbase.db')
    foto = '../img/tela.jpg'
else:
    operacoes = Operacoes('..\\DB\\dbase.db')
    foto = '..\\img\\tela.jpg'


class Acesso:

    def __init__(self, arquivo):
        self.conn = sqlite3.connect(arquivo)
        self.cursor = self.conn.cursor()

    # retorna o nome e senha do usuario solicitado
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
            print('buscaOperador = '+str(e))

    # verifica se existe usuario logado no sistema se existir retorna o nome e login,
    # senao returna False e será necessario entrar com um usuario
    def buscaOperadorAtivo(self):
        try:
            itens = []
            sql = "SELECT * FROM usuarios_historico where saida =''"
            self.cursor.execute(sql)
            contador = 0
            for linha in self.cursor.fetchall():
                contador += 1
                itens.append(linha)
            # print(itens)
            login, nome, saida = itens[0][1], itens[0][2], itens[0][4]
            if login:
                if saida == None or saida == '':
                    # print(login, nome, saida, sep=':')
                    return login, nome
                else:
                    return False, False
        except Exception as e:
            print('buscaOperadorAtivo = '+str(e))
            return False, False

    # faz a entrada do usuario no sistema
    def entraOperador(self, login, nome):

        try:
            sql = "INSERT INTO usuarios_historico (login,nome,entrada,saida) VALUES (?,?,?,?)"
            self.cursor.execute(
                sql, (login, nome, data, ""))
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def retiraOperador(self, login):
        try:
            sql = "UPDATE usuarios_historico SET saida=? WHERE login=? and saida=''"
            self.cursor.execute(sql, (data_e_hora_atuais, login))
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def verificaNivelUsuario(self, login, senha):
        try:
            itens = []
            sql = "SELECT * FROM usuarios where login =?"
            self.cursor.execute(sql, (login,))
            contador = 0
            for linha in self.cursor.fetchall():
                contador += 1
                itens.append(linha)
            nivel = itens[0][5]
            senh = str(itens[0][2])
            if senh == senha:
                return nivel
            else:
                return False
        except Exception as e:
            return False


if __name__ == '__main__':
    sistema = sys.platform
    if sistema == 'linux':
        acesso = Acesso('DB/dbase.db')
        foto = 'img/tela.jpg'
    else:
        acesso = Acesso('DB\\dbase.db')
        foto = 'img\\tela.jpg'

    # print(acesso.entraOperador('21220'))
    # print(acesso.buscaOperadorAtivo())
    print(acesso.verificaNivelUsuario('21220', '123456'))
    # print(acesso.retiraOperador('21220'))
    # print(acesso.entraOperador('21220', 'Christian'))
