# C:\Users\Christian\AppData\Roaming\Python\Python310\Scripts\pyuic5.exe -x .\tela.ui -o .\tela.py
# C:\Users\Christian\AppData\Roaming\Python\Python310\Scripts\pyinstaller.exe -F --console -w --upx-dir=D:\upx-4.0.2-win64 --distpath .\ --ico .\pdv.ico --name "SysPDV 2023" .\main.py
import importlib
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QWidget, QFormLayout
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont
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

        # self.setFixedSize(800, 600)

        self.frame_subtotal.hide()
        self.frame_login.hide()
        self.frame_logout.hide()
        self.frame_cancelaCupom.hide()
        self.frame_reducaoz.hide()

        # duplo clique na lista cancela o item
        self.lst_itens.itemDoubleClicked.connect(
            lambda: self.cancelaItem())

        # menu de acoes
        self.actionFimDia.triggered.connect(self.abreFrameRedZ)
        self.actionFinalizaCupom.triggered.connect(self.abreSubtotal)
        self.actionRetornar.triggered.connect(self.retornarTela)
        self.actionCancelaItem.triggered.connect(self.cancelaItem)
        self.actionCancelaCupom.triggered.connect(self.cancelaCupon)
        self.actionSaiOperador.triggered.connect(self.abreFrameLogout)
        self.actionEntraOperador.triggered.connect(self.abreFrameLogin)

        # acoes do subtotal
        self.rb_dinheiro.toggled.connect(
            lambda: self.calculaTroco("dinheiro"))
        self.rb_debito.toggled.connect(lambda: self.calculaTroco("debito"))
        self.rb_credito.toggled.connect(
            lambda: self.calculaTroco("credito"))
        self.rb_pix.toggled.connect(lambda: self.calculaTroco("pix"))
        self.ed_valorPago.textEdited.connect(lambda: self.exibeTroco())
        self.bt_finalizar.clicked.connect(lambda: self.fechaCupom(
            self.lb_total.text(), self.ed_valorPago.text(), self.lb_troco.text(), self.lbl_tipo_pagto.text()))

        self.txt_ean.setEnabled(False)
        self.txt_ean.returnPressed.connect(self.adicionaItem)

        # verifica se existe o usuario logado
        login, nome = False, False
        try:
            login, nome = acesso.buscaOperadorAtivo()

            self.txt_ean.setEnabled(True)
        except Exception as e:
            pass

        self.iniciaPDV(login=login, nome=nome)
        self.showMaximized()

    def iniciaPDV(self, login=False, nome=False):
        if login:
            self.lbl_rodape.setText(f'LOGIN: {login} - OPERADOR: {nome}')
            self.lbl_total.setText('R$ 0.00')
            self.lbl_item.setText('Caixa Livre')

            # verifica se existe cupom aberto
            self.verificaCupomAberto()

            # entrada de ean na passagem de compra
            self.txt_ean.setFocus()

        else:
            self.lbl_rodape.setText(f'Não Existe Operador Logado')
            login, nome = False, False
            self.lbl_total.setText('')
            self.txt_ean.setEnabled(False)
            self.lbl_item.setText('Caixa Fechado')

    # 1 abre o form de login e espera que o usuario preencha os dados
    def abreFrameLogin(self):
        login, nome = acesso.buscaOperadorAtivo()
        if not login:
            self.frame_login.show()
            self.frame_login.move(30, 54)
            self.ed_usuario_login.setText('')
            self.ed_senha_login.setText('')
            self.ed_senha_login.setEchoMode(QLineEdit.Password)
            self.ed_usuario_login.setFocus()
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
            self.lbl_mensagem.setText('')
            self.lbl_item.setText('Caixa Livre')
            self.frame_login.hide()
            self.frame_logout.hide()
            self.frame_reducaoz.hide()
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
            self.frame_reducaoz.hide()
            self.frame_logout.hide()
            self.txt_ean.setText('')
            # self.txt_ean.setFocus()

    # 1 abre o frame de logout
    def abreFrameLogout(self):
        # verifica se tem operador logado
        login, nome = acesso.buscaOperadorAtivo()
        self.ed_senha_logout.setEchoMode(QLineEdit.Password)
        if login:
            retorno = operacoes.listar_tudo(tabela='venda_tmp')
            if retorno:
                self.frame_logout.hide()
                self.frame_login.hide()
                self.frame_reducaoz.hide()
            else:
                self.frame_logout.show()
                self.frame_logout.move(30, 54)
                self.ed_usuario_logout.setText('')
                self.ed_senha_logout.setText('')
                self.ed_usuario_logout.setFocus()
                self.bt_saiOperador.clicked.connect(
                    lambda: self.tentaRetirarOperador(self.ed_usuario_logout.text(), self.ed_senha_logout.text()))

    # da a saida do operador no caixa
    def retiraOperador(self):
        self.frame_login.hide()
        self.frame_reducaoz.hide()
        self.frame_logout.show()
        self.frame_logout.move(30, 54)
        retorno = operacoes.listar_tudo(tabela='venda_tmp')
        self.bt_saiOperador.clicked.connect(
            lambda: self.tentaRetirarOperador(self.ed_usuario_logout.text(), self.ed_senha_logout.text()))
        if retorno:
            self.frame_logout.hide()
            self.frame_login.hide()
            self.frame_reducaoz.hide()
        else:
            # self.lbl_msg_login.setText(
            #     f"Digite o usuario para fazer o fechamento do caixa")
            self.ed_senha_login.setText('')
            self.ed_usuario_login.setText('')
            self.ed_usuario_login.setFocus()

    def tentaRetirarOperador(self, login, senha):
        try:
            blogin, bsenha, bnome = acesso.buscaOperador(login)
            if str(blogin) == str(login) and str(bsenha) == str(senha):
                retorno, qtd_linhas = acesso.retiraOperador(login)
                # print(qtd_linhas)
                if retorno:
                    if qtd_linhas > 0:
                        self.lbl_total.setText('')
                        self.lbl_item.setText('Caixa Fechado')
                        self.lbl_mensagem.setText('Não existe Operador Logado')
                        self.lbl_rodape.setText('')
                        self.frame_login.hide()
                        self.frame_logout.hide()
                        self.frame_reducaoz.hide()
                        self.txt_ean.setEnabled(False)
        except:
            self.frame_login.hide()
            self.frame_reducaoz.hide()
            self.frame_logout.hide()
            self.txt_ean.setEnabled(True)
            self.txt_ean.setFocus()
            self.lbl_mensagem.setText('Erro ao retirar o Operador')

    # verifica se existe cupom aberto
    def verificaCupomAberto(self):
        self.lst_itens.clear()
        total = float(0)
        retorno = operacoes.listar_tudo(tabela='venda_tmp')
        if retorno:
            self.lbl_item.setText('Cupom Aberto')
            for i in retorno:
                total += float(i[2])
                self.lst_itens.addItem(
                    f'{i[0]}\t{i[1]}\n\t\t\t\t1x R$ {i[2]}')

            total = "{:.2f}".format(total)
            self.lbl_total.setText(f'R$ {total}')
            self.lbl_mensagem.setText('Cupom aberto recuperado')

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
        self.frame_reducaoz.hide()

        self.ed_senha_cancelaCupom.setText('')
        self.ed_senha_login.setText('')
        self.ed_senha_logout.setText('')
        self.ed_usuario_cancelaCupom.setText('')
        self.ed_usuario_login.setText('')
        self.ed_usuario_logout.setText('')

        self.txt_ean.setEnabled(True)
        self.txt_ean.setFocus()

    # abertura do subtotal para fechamento do cupom
    def abreSubtotal(self):
        totalCompra = float(
            str(self.lbl_total.text()).replace('R$', '').strip())

        self.exibeTroco()

        if totalCompra > 0:
            self.lbl_item.setText('Subtotal')
            self.frame_subtotal.show()
            self.frame_subtotal.move(30, 54)
            self.lb_total.setText('R$ '+str("{:.2f}".format(totalCompra)))
            self.ed_valorPago.setText(str("{:.2f}".format(totalCompra)))
            self.ed_valorPago.setEnabled(False)
            self.bt_finalizar.setEnabled(False)
            self.txt_ean.setEnabled(False)

    # 1 se alguma opcao de radiobuttom foi acionada faz o calculo de troco
    def calculaTroco(self, tipo):
        totalCompra = self.lbl_total.text()
        self.ed_valorPago.setText(totalCompra)
        radioButton = self.sender()

        if radioButton.isChecked():
            self.bt_finalizar.setEnabled(True)
            self.lbl_tipo_pagto.setText(str(tipo).upper())
            troco = self.exibeTroco()
            if tipo == 'debito' or tipo == 'credito' or tipo == 'pix':
                self.ed_valorPago.setEnabled(False)
            elif tipo == 'dinheiro':
                self.ed_valorPago.setEnabled(True)
                self.ed_valorPago.setFocus()

    # 2 calcula o troco
    def exibeTroco(self):
        try:
            total = float(self.lb_total.text().replace('R$ ', ''))
            pago = float(self.ed_valorPago.text().replace(
                'R$ ', '').replace(',', '.'))
            troco = float(pago)-float(total)
            if troco >= 0:
                self.lb_troco.setText(f'R$ {"{:.2f}".format(troco)}')
                self.bt_finalizar.setEnabled(True)
            else:
                self.lb_troco.setText(f'Valor insulficiente')
                self.bt_finalizar.setEnabled(False)
            return troco
        except Exception as e:
            pass

    # adiciona item 'ativo' apos digitado na cupom
    def adicionaItem(self):
        self.lbl_mensagem.setText('')
        ean = self.txt_ean.text().replace('x', 'X').replace('*', 'X').split('X')
        if len(ean) > 1:
            qtd, ean = ean
        else:
            qtd, ean = 1, ean[0]
        if qtd == '':
            qtd = 1

        if str(ean).lower() == 'cf':  # cancela cupom
            self.txt_ean.setText('')
        elif str(ean).lower() == 'if':  # cancela item
            self.txt_ean.setText('')
        else:
            retorno = operacoes.buscarProduto(ean)
            if retorno[0] == 1:
                self.lbl_item.setText(
                    f' {qtd}x {retorno[2]} R$ {retorno[5]}')
                for i in range(int(qtd)):
                    total = self.lbl_total.text().replace('R$ ', '')
                    total = float(total)+float(retorno[5])
                    self.lbl_total.setText(f'R$ {"{:.2f}".format(total)}')

                    self.lst_itens.addItem(
                        f'{retorno[1]}\t{retorno[2]}\n\t\t\t\t1x R$ {retorno[5]}')
                    operacoes.addItemNaCompra(
                        retorno[1], retorno[2], retorno[5])
                    self.lst_itens.scrollToBottom()
                    self.txt_ean.setText('')
            else:
                QMessageBox.warning(
                    self, 'Aviso', f'Produto nao encontrado')
                self.txt_ean.setText('')

    # finaliza o cupom grava no bando e libera uma proxima compra
    def fechaCupom(self, total, pago, troco, forma):
        itens = operacoes.agrupaItensTmp()
        total = str(total).replace('R$ ', '')
        pago = str(pago).replace('R$ ', '')
        troco = str(troco).replace('R$ ', '')
        operador = str(self.lbl_rodape.text()).split(' ')[1]

        retorno = operacoes.cadastrarVenda(
            data, str(itens), total, forma, pago, troco, operador)
        if retorno:

            operacoes.limpaTemp()
            self.lst_itens.clear()
            self.txt_ean.setEnabled(True)
            self.txt_ean.setFocus()
            self.lbl_item.setText('Caixa Livre')
            self.lbl_total.setText('R$ 0.00')
            self.frame_subtotal.hide()
            self.lbl_mensagem.setText('Compra Finalizada!')
            valores = operacoes.verificaUltimoCupom()

            cupomImpresso = operacoes.criaCupom(valores[0])
            if not cupomImpresso:
                QMessageBox.warning(
                    self, 'Aviso', f'Cupom Finalizado!\nImpressora nao localizada')
        else:
            self.lbl_mensagem.setText('nao excluiu os temps')

    # remove algum item da lista da compra
    def cancelaItem(self):
        try:
            linhaSelecionada = self.lst_itens.currentItem().text()
            linhaSelecionada = linhaSelecionada.split('\t')
            ean = linhaSelecionada[0]
            produto = str(linhaSelecionada[1]).strip()

            ret = QMessageBox.question(
                self, 'ATENÇÃO!!!', f"Tem certeza que deseja cancelar o item:\n{ean} {produto} ", QMessageBox.Yes | QMessageBox.Cancel)

            if ret == QMessageBox.Yes:
                retorno = operacoes.remove_item_a_cancelar(ean)
                if retorno:
                    self.verificaCupomAberto()
                self.lbl_mensagem.setText(
                    f'Item {ean}-{produto} foi cancelado com sucesso!')
        except Exception as e:
            pass

    # faz o cancelamento do ultimo cupom finalizado
    def cancelaCupon(self):
        self.lbl_mensagem.setText('')
        retorno = operacoes.listar_tudo(tabela='venda_tmp')
        if not retorno:
            valores = operacoes.verificaUltimoCupom()
            if valores[1] == 'SIM':
                ret = QMessageBox.question(
                    self, 'ATENÇÃO!!!', f"Tem certeza que deseja cupom o item:\nCOO = {valores[0]}, Total do cupom = {valores[4]}", QMessageBox.Yes | QMessageBox.Cancel)

                if ret == QMessageBox.Yes:
                    self.autorizacaoCancelamento(valores[0])

                else:
                    self.lbl_mensagem.setText('Usuario ou senha invalido!')
            else:
                QMessageBox.warning(
                    self, 'ATENÇÃO!!!', f"Impossivel, o ultimo cupom ja esta cancelado!")

    def autorizacaoCancelamento(self, cupom):
        self.frame_cancelaCupom.show()
        self.frame_cancelaCupom.move(30, 54)
        self.txt_ean.setEnabled(False)
        self.ed_senha_cancelaCupom.setText('')
        self.ed_usuario_cancelaCupom.setText('')
        self.ed_usuario_cancelaCupom.setFocus()
        self.ed_senha_cancelaCupom.setEchoMode(QLineEdit.Password)
        self.bt_cancelaCupom.clicked.connect(lambda: self.tentaCancelaCupom(
            self.ed_usuario_cancelaCupom.text(), self.ed_senha_cancelaCupom.text(), cupom))

    def tentaCancelaCupom(self, login, senha, cupom):
        retorno = False
        nivel = False
        nivel, nome = acesso.verificaNivelUsuario(login, senha)
        if nivel == 'GERENTE':
            retorno, status = operacoes.cancelaCupom(cupom)
            if retorno:
                if status == 'SIM':
                    QMessageBox.information(
                        self, 'ATENÇÃO!!!', f"Cupom Cancelado!")
                    operacoes.criaCupom(cupom)
                    self.frame_cancelaCupom.hide()
                    self.txt_ean.setEnabled(True)
                    self.txt_ean.setText('')
                    self.txt_ean.setFocus()
            else:
                QMessageBox.warning(self, 'ATENÇÃO!!!',
                                    f"Erro ao cancelar")
                self.frame_cancelaCupom.hide()
                self.txt_ean.setEnabled(True)
                self.txt_ean.setFocus()
        else:
            self.lbl_mensagem.setText('Usuario ou senha invalido!')
            self.frame_cancelaCupom.hide()
            self.txt_ean.setEnabled(True)
            self.txt_ean.setFocus()

    # 1 abre frame fim do dia
    def abreFrameRedZ(self):
        login, nome = acesso.buscaOperadorAtivo()
        # print(login, nome)
        self.ed_senha_logout.setEchoMode(QLineEdit.Password)
        if not login:
            self.frame_reducaoz.show()
            self.ed_usuario_z.setText('')
            self.ed_senha_z.setText('')
            self.ed_usuario_z.setFocus()
            self.bt_z.clicked.connect(
                lambda: self.geraFimDia(self.ed_usuario_z.text(), self.ed_senha_z.text()))

    # 2 verfica senha
    def geraFimDia(self, login, senha):
        retorno = False
        nivel = False
        nivel, nome = acesso.verificaNivelUsuario(login, senha)
        if nivel == 'GERENTE':
            retorno = operacoes.criaCupom(login=nome, reducaoz=True)
            if retorno:
                # if status == 'SIM':
                QMessageBox.information(
                    self, 'ATENÇÃO!!!', f"Relatorio de Fim do dia impresso!")
                self.lbl_mensagem.setText('')
                self.frame_reducaoz.hide()
                self.txt_ean.setEnabled(False)

            else:
                QMessageBox.warning(self, 'ATENÇÃO!!!',
                                    f"Relatorio de Fim do dia impresso!\n\nErro ao Imprimir o documento")
                self.frame_reducaoz.hide()
                self.txt_ean.setEnabled(False)

        else:
            self.lbl_mensagem.setText('Usuario ou senha invalido!')
            self.frame_reducaoz.hide()
            self.txt_ean.setEnabled(False)


qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
