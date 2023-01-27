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

        self.moduloAtivo = 'login'
        self.isMaximized()
        # self.resize(self.sizeHint().width,self.size().height() + content.sizeHint().height());
        # self.gridLayout_4.setAlignment()
        self.frame_modulo_login.hide()
        self.frame_modulo_produtos.hide()
        self.frame_logout.show()
        self.frame_cupom.hide()

        self.actionProdutos.triggered.connect(lambda: self.abreFrameProdutos())
        self.actionUsuario.triggered.connect(lambda: self.abreFrameUsuarios())
        self.actionCabecalho_Cupom.triggered.connect(
            lambda: self.abreFrameCupom('topo'))
        self.actionRodape_Cupom.triggered.connect(
            lambda: self.abreFrameCupom('rodape'))
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

    # 1 produtos
    def abreFrameProdutos(self):
        if not self.moduloAtivo == 'produtos':
            self.moduloAtivo = 'produtos'
            self.frame_modulo_produtos.show()
            self.frame_modulo_produtos.move(50, 50)
            self.frame_modulo_login.hide()
            self.frame_cupom.hide()

            self.bt_cadastro_produto.setText('Cadastrar')
            # self.bt_cadastro_produto.clicked.connect(lambda: )
            self.ed_ean.setText('')
            self.ed_produto.setText('')
            self.ed_qtd.setText('')
            self.ed_valor_custo.setText('')
            self.ed_valor_venda.setText('')
            self.bt_cadastro_produto.setText('Cadastrar')

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
            self.bt_cadastro_produto.setText('Cadastrar')
            self.retornaProdutos()
        # else:
        #     QMessageBox.warning(
        #         self, 'Aviso', f'Erro ao cadastrar o Produto\nCODIGO EAN JA EM USO')

    # retorna todos os produtos
    def retornaProdutos(self):
        self.lst_produtos.clear()
        retorno = operacoes.listar_tudo(tabela='produtos')
        if retorno:
            for i in retorno:
                print(i[1])
                if i[1] == 1:
                    ativo = 'SIM'
                else:
                    ativo = 'NAO'
                self.lst_produtos.addItem(
                    f'{i[2]: <13}\t{i[3]: <50}\tEstoque:{i[4]: <5}\tCusto: R${i[5]: <5}\tVenda: R${i[6]: <10}\tAtivo:{ativo}')

    def editaProdutos(self):
        ean, produto, estoque, custo, venda, ativo = str(
            self.lst_produtos.currentItem().text()).split('\t')
        if ativo.split(':')[1] == 'SIM':
            self.cb_ativo_produto.setCurrentText('SIM')
            print('sim')
        else:
            print('nao')
            self.cb_ativo_produto.setCurrentText('NAO')
        self.ed_ean.setText(ean.strip())
        self.ed_produto.setText(produto.strip())
        self.ed_qtd.setText(str(estoque.strip()).split(':')[1])
        self.ed_valor_custo.setText(
            str(custo.strip()).replace(' R$', '').split(':')[1])
        self.ed_valor_venda.setText(
            str(venda.strip()).replace(' R$', '').split(':')[1])
        self.bt_cadastro_produto.setText('ATUALIZAR')

    # 1 usuarios
    def abreFrameUsuarios(self):
        if not self.moduloAtivo == 'usuarios':
            self.moduloAtivo = 'usuarios'
            self.frame_modulo_login.show()
            self.frame_modulo_login.move(50, 50)
            self.frame_modulo_produtos.hide()
            self.frame_logout.hide()
            self.frame_cupom.hide()

            self.bt_cadastro_usuario.setText('Cadastrar')
            # self.bt_cadastro_produto.clicked.connect(lambda: )
            self.ed_login.setText('')
            self.ed_senha.setText('')
            self.ed_nome.setText('')
            self.ed_cpf.setText('')

            self.bt_cadastro_produto.setText('Cadastrar')

            self.retornaUsuarios()
            self.cb_ativo.addItems(['SIM', 'NAO'])
            self.cb_funcao.addItems(['Operador', 'Gerente'])
            self.bt_cadastro_usuario.clicked.connect(
                lambda: self.cadastroUsuarios())

            # duplo clique na lista cancela o item
            self.lst_usuarios.itemDoubleClicked.connect(
                lambda: self.editaUsuarios())

    # 2 produtos
    def cadastroUsuarios(self):
        retorno = operacoes.cadastrarUsuario(self.cb_ativo.currentText(), self.ed_login.text(
        ), self.ed_senha.text(), self.ed_nome.text(), self.ed_cpf.text(), self.cb_funcao.currentText(), self.bt_cadastro_usuario.text())
        if retorno:
            QMessageBox.information(
                self, 'Aviso', f'Cadastro feito com sucesso')
            self.ed_login.setText('')
            self.ed_senha.setText('')
            self.ed_nome.setText('')
            self.ed_cpf.setText('')
            self.bt_cadastro_produto.setText('Cadastrar')
            self.retornaUsuarios()
        # else:
        #     QMessageBox.warning(
        #         self, 'Aviso', f'Erro ao cadastrar o Produto\nCODIGO EAN JA EM USO')

    # retorna todos os produtos
    def retornaUsuarios(self):
        self.lst_usuarios.clear()
        retorno = operacoes.listar_tudoUsuario(tabela='usuarios')
        if retorno:
            for i in retorno:

                if i[0] == 1:
                    ativo = 'SIM'
                else:
                    ativo = 'NAO'
                if i[1] != None:
                    self.lst_usuarios.addItem(
                        f'{i[1]: <6}\t{i[3]: <20}\t{i[4]: <10}\t{i[5]: <10}\t Ativo:{ativo}')

    def editaUsuarios(self):
        login, nome, cpf, funcao, ativo = str(
            self.lst_usuarios.currentItem().text()).split('\t')
        if ativo.split(':')[1] == 'SIM':
            self.cb_ativo_produto.setCurrentText('SIM')
            print('sim')
        else:
            print('nao')
            self.cb_ativo_produto.setCurrentText('NAO')
        self.ed_login.setText(login.strip())
        self.ed_nome.setText(nome.strip())
        self.ed_cpf.setText(cpf.strip())
        self.cb_funcao.setCurrentText(funcao.strip())
        self.bt_cadastro_usuario.setText('ATUALIZAR')

    def abreFrameCupom(self, tipo):
        if not self.moduloAtivo == 'cupom':
            self.moduloAtivo = 'cupom'
            self.frame_cupom.show()
            self.frame_logout.hide()
            self.frame_modulo_login.hide()
            self.frame_modulo_produtos.hide()

        if tipo == 'topo':
            self.lbl_titulo_cupom.setText('Editar o cabeçalho do Cupom')
            with open('..//PDV//CONFIG//cupom1.txt', 'r') as r:
                r = r.read()

                self.ed_cupom.setPlainText(r)
        else:
            self.lbl_titulo_cupom.setText('Editar o rodapé do Cupom')
            with open('..//PDV//CONFIG//cupom2.txt', 'r') as r:
                r = r.read()

                self.ed_cupom.setPlainText(r)


qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
