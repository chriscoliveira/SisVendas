import sqlite3
from time import sleep
import os
import re
import sys

sistema = sys.platform
if sistema == 'linux':
    nome_cupom = 'CUPOM/cupom_'
    porta_com = '/dev/ttyACM0'
else:
    nome_cupom = 'CUPOM\\cupom_'
    porta_com = 'COM1'


class Operacoes:

    def __init__(self, arquivo):
        self.conn = sqlite3.connect(arquivo)
        self.cursor = self.conn.cursor()

    def cadastrarProduto(self, ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra):
        try:
            ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra = str(ativo).upper(), str(ean).upper(), str(
                produto).upper(), str(quantidade).upper(), str(valor_custo).upper().replace(',', '.'), str(valor_venda).upper().replace(',', '.'), str(ultima_compra).upper()
            sql = "INSERT INTO produtos (ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra) VALUES (?,?,?,?,?,?,?)"
            self.cursor.execute(
                sql, (ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra))
            self.conn.commit()
            return f"O {produto=} {ean=} foi cadastrado com sucesso!"
        except Exception as e:
            return f"Ocorreu um erro ao cadastrar = {e}"

    def addItemNaCompra(self, ean, produto, valor):
        try:
            sql = "INSERT INTO venda_tmp (ean, produto,valor) VALUES (?,?,?)"
            self.cursor.execute(
                sql, (ean, produto, valor))
            self.conn.commit()
            return f"O {produto=} {ean=} foi adicionado!"
        except Exception as e:
            return f"Ocorreu um erro ao adicionar = {e}"

    # cadastra a venda na tabela vendas
    def cadastrarVenda(self, data, itens, total_compra, forma_pagamento, pago, troco):
        # total_compra ="{:.2f}".format(total_compra)
        # pago ="{:.2f}".format(pago)
        # troco ="{:.2f}".format(troco)
        try:
            sql = "INSERT INTO vendas (data, itens,total_compra,forma_pagamento,valor_pago,troco) VALUES (?,?,?,?,?,?)"
            self.cursor.execute(
                sql, (data, itens, total_compra, forma_pagamento, pago, troco))
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def editar(self, id, ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra):
        try:
            ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra = str(ativo).upper(), str(ean).upper(), str(
                produto).upper(), str(quantidade).upper(), str(valor_custo).upper().replace(',', '.'), str(valor_venda).upper().replace(',', '.'), str(ultima_compra).upper()
            sql = "UPDATE produtos SET ativo=?, ean=?, produto=?, quantidade=?, valor_custo=?, valor_venda=?, ultima_compra=? WHERE id=?"
            self.cursor.execute(sql, (ativo, ean, produto, quantidade,
                                valor_custo, valor_venda, ultima_compra, id))
            self.conn.commit()
            return f"O {produto=} {ean=} foi alterado com sucesso!"
        except Exception as e:
            return f"Ocorreu um erro ao alterar = {e}"

    def listar_tudo(self, tabela):
        itens = []
        sql = "SELECT ean,produto,valor FROM "+tabela
        self.cursor.execute(sql)
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        return itens

    def remove_item_a_cancelar(self, ean):
        itens = []
        sql = "SELECT id,ean,produto,valor FROM venda_tmp where ean = ?"
        self.cursor.execute(sql, (ean,))
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)

        id = 0
        for i in itens:
            id = i[0]
        print(id)
        retorno = self.remove_produto_selecionado('venda_tmp', id)
        return retorno

    def remove_produto_selecionado(self, tabela, id):
        sql = "DELETE FROM "+tabela+" WHERE id=?"
        self.cursor.execute(sql, (id,))
        self.conn.commit()
        afetado = self.cursor.rowcount
        if afetado > 0:
            return True
        else:
            return False

    def agrupaItensTmp(self, ):
        itens = []
        sql = "select count(ean),ean,produto,sum(valor) from venda_tmp group by ean"
        self.cursor.execute(sql)
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        return itens

    def buscarProduto(self, termo):
        print(termo)
        try:
            contador = 0
            sql = "SELECT * FROM produtos WHERE ean = ?"
            # termo = f'%{termo}%'
            self.cursor.execute(
                sql, (termo,))

            for linha in self.cursor.fetchall():
                contador += 1
                # print(linha)
                id = linha[0]
                ean = linha[1]
                produto = linha[2]
                quantidade = linha[3]
                valor_custo = linha[4]
                valor_venda = linha[5]
                ultima_compra = linha[6]

            return ean, produto, quantidade, valor_custo, valor_venda, ultima_compra, contador
        except Exception as e:
            return '', '', '', '', '', '', ''

    def limpaTemp(self):
        sql = "DELETE FROM venda_tmp"
        self.cursor.execute(sql)
        self.conn.commit()

    def verificaUltimoCupom(self):
        sql = 'SELECT * FROM vendas ORDER BY coo DESC limit 1'
        return self.cursor.execute(sql).fetchall()[0]

    def cancelaCupom(self, coo):
        sql_busca = 'select * from vendas where coo=?'
        self.cursor.execute(
            sql_busca, (coo,))
        cancelado = ''
        for linha in self.cursor.fetchall():
            print(linha[1])
            cancelado = linha[1]

        sql = "UPDATE vendas SET ativo='CANCELADO' WHERE coo=?"
        self.cursor.execute(sql, (coo,))
        self.conn.commit()
        afetado = self.cursor.rowcount
        if afetado > 0:
            return True, cancelado
        else:
            return False, False

    def criaCupom(self, coo, cancelado=False):
        sql_busca = 'select * from vendas where coo=?'
        self.cursor.execute(
            sql_busca, (coo,))

        for linha in self.cursor.fetchall():
            print(linha)
            coo = linha[0]
            ativo = linha[1]
            data = linha[2]
            itens = eval(linha[3])
            total = linha[4]
            forma = linha[5]
            pago = linha[6]
            troco = linha[7]
        with open(f'CONFIG/cupom1.txt', 'r') as inicioCupom:
            inicioCupom = inicioCupom.readlines()

            with open(f'CONFIG/cupom2.txt', 'r') as fimCupom:
                fimCupom = fimCupom.readlines()

                with open(f'{nome_cupom}.txt', 'w') as e:

                    # escreve o inicio do cupom
                    for inicio in inicioCupom:
                        e.write(inicio.replace('{coo}', str(coo)))
                    if ativo == 'CANCELADO':
                        e.write(f'Cupom No{coo} foi cancelado em {data}\n')
                    else:
                        # itens
                        for i in itens:
                            tot = float(i[3] / i[0])
                            valor = float(i[3])
                            # escreve os itens da compra
                            e.write(
                                f'{i[1]} {i[2]}\n        {i[0]} X {"{:.2f}".format(tot)} = R${"{:.2f}".format(valor)}\n')

                    # escreve o fim do cupom
                    for fim in fimCupom:
                        e.write(fim.replace('{total}', str(total)).replace('{forma}', str(forma)).replace(
                            '{pago}', str(pago)).replace('{troco}', str(troco)).replace('{data}', str(data)))

                    # os.system(f'cat cupom.txt > /dev/ttyACM0')
        import serial

        ser = serial.Serial(porta_com, 9600)
        with open(f'{nome_cupom}.txt', 'r') as f:
            text = f.read()

        ser.write(text.encode())

        return f'{nome_cupom}.txt'


if __name__ == "__main__":
    sistema = sys.platform
    if sistema == 'linux':
        operacoes = Operacoes('../DB/dbase.db')
        foto = 'img/tela.jpg'
    else:
        operacoes = Operacoes('..\\DB\\dbase.db')
        foto = 'img\\tela.jpg'

    # retorno = operacoes.inserir(
    #     "1", "7891234", 'acucar', '10', '1,00', '4,50', '')
    # print(retorno)

    # retorno = operacoes.editar(
    #     '5', '0', '123', 'cafe', '12', '8,00', '13,01', '')
    # retorno = operacoes.remover('7')
    # print(retorno)

    # retorno = operacoes.listar_tudo(tabela='venda_tmp')
    # # retorno = operacoes.agrupaItensTmp()
    # print(retorno)

    # # retorno = operacoes.buscar('789123')
    # retorno = operacoes.remove_item_a_cancelar('789')
    # retorno = operacoes.cadastrarVenda(
    #     '20-01-2023', 'aaaaaa', '50', 'dinheiro', '25')
    # retorno = operacoes.verificaUltimoCupom()
    retorno = operacoes.criaCupom('15')
    print(retorno)
    # import serial

    # ser = serial.Serial('/dev/ttyACM0', 9600)
    # with open(f'CUPOM/cupom_7.txt', 'r') as f:
    #     text = f.read()
    # ser.write(text.encode())
