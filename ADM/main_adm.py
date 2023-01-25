# C:\Users\Christian\AppData\Roaming\Python\Python310\Scripts\pyuic5.exe -x .\tela.ui -o .\tela.py

import importlib
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
import os
from tela import *
import sys
from operacoes_db import *
from acesso import *
from datetime import *

sistema = sys.platform
if sistema == 'linux':
    operacoes = Operacoes('../DB/dbase.db')
    acesso = Acesso('../DB/dbase.db')
    foto = '../img/tela.jpg'
else:
    operacoes = Operacoes('..\\DB\\dbase.db')
    foto = '..\\img\\tela.jpg'
    acesso = Acesso('..\\DB\\dbase.db')

data_e_hora_atuais = datetime.now()
data_atual = date.today()
data = data_e_hora_atuais.strftime('%d-%m-%Y %H:%M:%S')


class Novo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)

        self.setFixedSize(1200, 800)
        self.frame_modulo_login.hide()
        self.frame_modulo_produtos.hide()
        self.frame_logout.hide()

        self.actionProdutos.triggered.connect(lambda: self.abreFrameProdutos())
        # duplo clique na lista cancela o item
        # self.lst_itens.itemDoubleClicked.connect(
        #     lambda: self.cancelaItem())

    # 1 abre o form de login e espera que o usuario preencha os dados

    def abreFrameLogin(self):
        login, nome = acesso.buscaOperadorAtivo()
        if not login:

            self.bt_entraOperador.clicked.connect(
                lambda: self.entraOperador(log=self.ed_usuario_login.text(), sen=self.ed_senha_login.text()))

    # 2 recebe os dados e envia para comparação
    def entraOperador(self, log, sen):
        try:
            login, senha, nome = acesso.buscaOperador(log)
            self.verificaSenhaCorreta(
                senhadigitada=sen, senhabanco=senha, login=log, nome=nome)
        except:
            self.txt_ean.setText('')
            self.lbl_mensagem.setText('Usuario invalido! Tente novamente')
            self.lbl_rodape.setText('')

    # 3 compara e libera o uso
    def verificaSenhaCorreta(self, senhadigitada, senhabanco, login, nome):
        if str(senhabanco) == str(senhadigitada):
            self.lbl_rodape.setText(f'LOGIN: {login} - OPERADOR: {nome}')
            self.lbl_total.setText('R$ 0.00')
            self.lbl_item.setText('Caixa Livre')
            self.frame_login.hide()
            self.frame_logout.hide()
            self.txt_ean.setFocus()
            retorno = acesso.entraOperador(login, nome)
            if retorno:
                login, nome = acesso.buscaOperadorAtivo()
                self.txt_ean.setEnabled(True)
                self.txt_ean.setFocus()
            else:
                self.lbl_mensagem.setText('Erro ao entrar o operador')
            self.txt_ean.setText('')
        else:
            self.lbl_item.setText('Caixa Fechado')
            self.lbl_mensagem.setText('Senha Inválida')
            self.frame_login.hide()
            self.frame_logout.hide()
            self.txt_ean.setText('')

    # retorna a tela inicial
    def retornarTela(self):
        self.rb_debito.setCheckable(False)
        self.rb_credito.setCheckable(False)
        self.rb_dinheiro.setCheckable(False)
        self.rb_pix.setCheckable(False)

        self.rb_debito.setCheckable(True)
        self.rb_credito.setCheckable(True)
        self.rb_dinheiro.setCheckable(True)
        self.rb_pix.setCheckable(True)

        self.frame_subtotal.hide()
        self.frame_logout.hide()
        self.frame_login.hide()
        self.frame_cancelaCupom.hide()

        self.ed_senha_cancelaCupom.setText('')
        self.ed_senha_login.setText('')
        self.ed_senha_logout.setText('')
        self.ed_usuario_cancelaCupom.setText('')
        self.ed_usuario_login.setText('')
        self.ed_usuario_logout.setText('')

        self.txt_ean.setEnabled(True)
        self.txt_ean.setFocus()

    # 1 produtos
    def abreFrameProdutos(self):
        self.frame_modulo_produtos.show()
        self.frame_modulo_produtos.move(50, 50)
        self.bt_cadastro_produto.setText('Cadastrar')
        # self.bt_cadastro_produto.clicked.connect(lambda: )

        self.retornaProdutos()

        self.cb_ativo_produto.addItems(['SIM', 'NAO'])
        self.bt_cadastro_produto.clicked.connect(
            lambda: self.cadastroProdutos())

        # duplo clique na lista cancela o item
        self.lst_produtos.itemDoubleClicked.connect(
            lambda: self.editaProdutos())

    # 2 produtos
    def cadastroProdutos(self):
        retorno = operacoes.cadastrarProduto(self.cb_ativo_produto.currentText(
        ), self.ed_ean.text(), self.ed_produto.text(), self.ed_qtd.text(), self.ed_valor_custo.text(), self.ed_valor_venda.text(), '', self.bt_cadastro_produto.text())
        if retorno:
            QMessageBox.information(
                self, 'Aviso', f'Cadastro feito com sucesso')
            self.ed_ean.setText('')
            self.ed_produto.setText('')
            self.ed_qtd.setText('')
            self.ed_valor_custo.setText('')
            self.ed_valor_venda.setText('')
        else:
            QMessageBox.warning(
                self, 'Aviso', f'Erro ao cadastrar o Produto\nCODIGO EAN JA EM USO')

    # retorna todos os produtos
    def retornaProdutos(self):
        self.lst_produtos.clear()
        retorno = operacoes.listar_tudo(tabela='produtos')
        if retorno:
            for i in retorno:
                if i[1] == '0':
                    ativo = 'SIM'
                else:
                    ativo = 'NAO'
                self.lst_produtos.addItem(
                    f'{i[2]}\t{i[3]}\tEstoque:{i[4]}\tCusto: R${i[5]}\tVenda: R${i[6]}')

    def editaProdutos(self):
        ean, produto, estoque, custo, venda = str(
            self.lst_produtos.currentItem().text()).split('\t')
        self.ed_ean.setText(ean)
        self.ed_produto.setText(produto)
        self.ed_qtd.setText(str(estoque).split(':')[1])
        self.ed_valor_custo.setText(
            str(custo).replace(' R$', '').split(':')[1])
        self.ed_valor_venda.setText(
            str(venda).replace(' R$', '').split(':')[1])
        self.bt_cadastro_produto.setText('ATUALIZAR')


qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
