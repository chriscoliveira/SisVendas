# C:\Users\Christian\AppData\Roaming\Python\Python310\Scripts\pyuic5.exe -x .\tela.ui -o .\tela.py

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
    operacoes = Operacoes('DB/dbase.db')
    acesso = Acesso('DB/dbase.db')
    foto = 'img/tela.jpg'
else:
    operacoes = Operacoes('DB\\dbase.db')
    foto = 'img\\tela.jpg'
    acesso = Acesso('DB\\dbase.db')

data_e_hora_atuais = datetime.now()
data_atual = date.today()
data = data_e_hora_atuais.strftime('%d-%m-%Y %H:%M:%S')

import importlib



class Novo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)

        self.setFixedSize(1200, 800)
        self.frame_subtotal.hide()
        self.frame_login.hide()
        self.frame_logout.hide()

        # duplo clique na lista cancela o item
        self.lst_itens.itemDoubleClicked.connect(
            lambda: self.cancelaItem())

        # menu de acoes
        self.actionFinalizaCupom.triggered.connect(self.abreSubtotal)
        self.actionRetornar.triggered.connect(self.retornarTela)
        self.actionCancelaItem.triggered.connect(self.cancelaItem)
        self.actionCancelaCupom.triggered.connect(self.cancelaCupon)
        self.actionSaiOperador.triggered.connect(self.retiraOperador)
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
        
        self.txt_ean.returnPressed.connect(self.adicionaItem)
        self.bt_saiOperador.clicked.connect(
                lambda: self.tentaRetirarOperador(self.ed_usuario_logout.text(),self.ed_senha_logout.text()))
        
        
        # verifica se existe o usuario logado
        login, nome = False, False
        try:
            login, nome = acesso.buscaOperadorAtivo()
            print(f'{login=}{nome=}')
        except Exception as e:
            print(f'{login=}{nome=}')
            print('nao ha operador atvio '+e)

        
        self.iniciaPDV(login=login, nome=nome)

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
            self.lbl_item.setText('Caixa Fechado')
            self.txt_ean.setFocus()
            # self.txt_ean.returnPressed.connect(
            #     lambda: self.entraOperador(self.txt_ean.text()))
    
    # 1 abre o form de login e espera que o usuario preencha os dados
    def abreFrameLogin(self):
        self.frame_login.show()
        self.frame_login.move(30, 54)
        self.ed_senha_login.setText('')
        self.ed_senha_login.setFocus()
        self.bt_entraOperador.clicked.connect(
                lambda: self.entraOperador(log=self.ed_usuario_login.text(), sen=self.ed_senha_login.text()))
        # self.ed_senha_login.returnPressed.connect(
        # lambda: self.entraOperador(log=self.ed_usuario_login.text(), sen=self.ed_senha_login.text()))
            
    # 2 recebe os dados e envia para comparação
    def entraOperador(self,log,sen):
        print('entraOperador',log,sen)
        try:
            login, senha, nome = acesso.buscaOperador(log)
            self.verificaSenhaCorreta(senhadigitada=sen, senhabanco=senha,login=log,nome=nome)
            # self.frame_login.show()
            # self.frame_login.move(30, 54)
            # self.lbl_msg_login.setText(
            #     f"Digite a senha para o usuario: {login}")
            pass
            
        except:
            self.txt_ean.setText('')
            self.txt_ean.setFocus()
            self.lbl_rodape.setText(
                'Caixa Fechado, Usuario invalido! Tente novamente ')

    # 3 compara e libera o uso
    def verificaSenhaCorreta(self, senhadigitada, senhabanco, login, nome):
        if str(senhabanco) == str(senhadigitada):
            self.lbl_rodape.setText(f'LOGIN: {login} - OPERADOR: {nome}')
            self.lbl_total.setText('R$ 0.00')
            self.lbl_item.setText('Caixa Livre')
            self.frame_login.hide()
            # with open('operador.txt', 'w') as arq:
            #     arq.write(f'login={login},{nome}\n')
            retorno = acesso.entraOperador(login, nome)
            if retorno:
                login, nome = acesso.buscaOperadorAtivo()
                print('entrou '+login+' - '+nome)
                print('operador entrou no sistema')
                
                self.iniciaPDV(login, nome)

            else:
                print('erro ao entrar o operador')
            self.txt_ean.setText('')
            self.txt_ean.setFocus()
        else:
            self.lbl_item.setText('Caixa Fechado - Senha Inválida')
            self.frame_login.hide()
            self.txt_ean.setText('')
            self.txt_ean.setFocus()

    # da a saida do operador no caixa
    def retiraOperador(self):
        self.frame_logout.show()
        self.frame_logout.move(30, 54)
        retorno = operacoes.listar_tudo(tabela='venda_tmp')
        if retorno:
            self.frame_logout.hide()
        else:
            # self.lbl_msg_login.setText(
            #     f"Digite o usuario para fazer o fechamento do caixa")
            self.ed_senha_login.setText('')
            self.ed_usuario_login.setText('')
            self.ed_usuario_login.setFocus()
            
    def tentaRetirarOperador(self, login,senha):
        print(login,senha)
        blogin, bsenha, bnome = acesso.buscaOperador(login)
        if str(blogin) == str(login) and str(bsenha) == str(senha):
            print(f'{blogin=} {login=} {bsenha} {senha}')
            retorno = acesso.retiraOperador(login)
            print(retorno)
            if retorno:
                self.lbl_total.setText('')
                self.lbl_item.setText('Caixa Fechado')
                self.lbl_rodape.setText('Não existe Operador Logado')
                self.txt_ean.setFocus()
                self.frame_login.hide()
        else:
            print(f'R={blogin=} {login=} {bsenha} {senha}')
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

        # self.lbl_item.setText('Cupom Aberto')
        self.frame_subtotal.hide()
        # self.frame_login.show()
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
            # if troco>0:
            #     print(troco,type(troco))
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
            # troco = "{:.2f}".format(troco)
            # self.ed_valorPago.setText(f'R$ {pago}')
            # print(troco)
            if troco >= 0:
                self.lb_troco.setText(f'R$ {"{:.2f}".format(troco)}')
                self.bt_finalizar.setEnabled(True)
            else:
                self.lb_troco.setText(f'Valor insulficiente')
                self.bt_finalizar.setEnabled(False)
            return troco
        except Exception as e:
            print(e)

    # adiciona item 'ativo' apos digitado na cupom
    def adicionaItem(self):
        ean = self.txt_ean.text().replace('x', 'X').split('X')
        if len(ean) > 1:
            qtd, ean = ean
        else:
            qtd, ean = 1, ean[0]

        if str(ean).lower() == 'cf':  # cancela cupom
            self.txt_ean.setText('')
            print('cancela cupom')
        elif str(ean).lower() == 'if':  # cancela item
            self.txt_ean.setText('')
            print('cancela item')
        else:
            retorno = operacoes.buscarProduto(ean)
            print(f'{retorno=}')

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
        print(f'{total=} {pago=} {troco=} {forma=} {itens=} {data=}')
        retorno = operacoes.cadastrarVenda(
            data, str(itens), total, forma, pago, troco)
        print(retorno)
        if retorno:
            operacoes.limpaTemp()
            self.lst_itens.clear()
            self.txt_ean.setEnabled(True)
            self.txt_ean.setFocus()
            self.lbl_item.setText('Caixa Livre')
            self.lbl_total.setText('R$ 0.00')
            self.frame_subtotal.hide()
        else:
            print('nao excluiu os temps')

    # remove algum item da lista da compra
    def cancelaItem(self):
        try:
            linhaSelecionada = self.lst_itens.currentItem().text()
            linhaSelecionada = linhaSelecionada.split('\t')
            ean = linhaSelecionada[0]
            produto = linhaSelecionada[1]

            ret = QMessageBox.question(
                self, 'ATENÇÃO!!!', f"Tem certeza que deseja cancelar o item:\n{ean} {produto} ", QMessageBox.Yes | QMessageBox.Cancel)

            if ret == QMessageBox.Yes:
                retorno = operacoes.remove_item_a_cancelar(ean)
                print(retorno)
                if retorno:
                    self.verificaCupomAberto()
        except Exception as e:
            pass

    # faz o cancelamento do ultimo cupom finalizado
    def cancelaCupon(self):
        valores = operacoes.verificaUltimoCupom()
        if valores[1] == 'SIM':
            ret = QMessageBox.question(
                self, 'ATENÇÃO!!!', f"Tem certeza que deseja cupom o item:\nCOO = {valores[0]}, Total do cupom = {valores[4]}", QMessageBox.Yes | QMessageBox.Cancel)

            if ret == QMessageBox.Yes:
                retorno = operacoes.cancelaCupom(valores[0])
                if retorno:
                    QMessageBox.information(
                        self, 'ATENÇÃO!!!', f"Cupom Cancelado!")
                else:
                    QMessageBox.warning(self, 'ATENÇÃO!!!',
                                        f"Erro ao cancelar")
        else:
            QMessageBox.warning(
                self, 'ATENÇÃO!!!', f"Impossivel, o ultimo cupom ja esta cancelado!")


qt = QApplication(sys.argv)

novo = Novo()
novo.show()
qt.exec_()
