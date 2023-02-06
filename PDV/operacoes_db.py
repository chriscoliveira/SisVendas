import sqlite3
from time import sleep
import os
import re
import sys
from datetime import date, datetime

sistema = sys.platform
if sistema == 'linux':
    nome_cupom = 'CUPOM/cupom_'
    porta_com = '/dev/ttyACM0'
else:
    nome_cupom = 'CUPOM\\cupom_'
    porta_com = 'COM1'

data_e_hora_atuais = datetime.now()
data_atual = date.today()
data = data_e_hora_atuais.strftime('%d-%m-%Y %H:%M:%S')
dataResumida = data_e_hora_atuais.strftime('%d-%m-%Y')


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
    def cadastrarVenda(self, data, itens, total_compra, forma_pagamento, pago, troco, operador):
        # total_compra ="{:.2f}".format(total_compra)
        # pago ="{:.2f}".format(pago)
        # troco ="{:.2f}".format(troco)
        try:
            # cadastra a venda
            sql = "INSERT INTO vendas (data, itens,total_compra,forma_pagamento,valor_pago,troco,operador) VALUES (?,?,?,?,?,?,?)"
            self.cursor.execute(
                sql, (data, itens, total_compra, forma_pagamento, pago, troco, operador))
            self.conn.commit()

            # baixa o estoque
            try:
                item = eval(itens)
                for i in item:
                    qtd = i[0]
                    cod = i[1]
                    # print(f'{qtd=} {cod=}')
                    # recebe o estoque atual do produto
                    sql = "SELECT * FROM produtos WHERE ean = ?"
                    # termo = f'%{termo}%'
                    self.cursor.execute(
                        sql, (cod,))

                    for linha in self.cursor.fetchall():
                        quantidade = linha[4]
                    # print(f'{quantidade=}')
                    qtd = int(quantidade)-int(qtd)
                    sql = "UPDATE produtos set quantidade=? where ean=?"
                    self.cursor.execute(sql, (qtd, cod))
                    self.conn.commit()

            except Exception as e:
                print(e)
            #     qtd, ean, produto, preco = i.split(',')
            #     print(qtd, ean, produto, sep='>')
            # sql = "UPDATE produtos set quantidade=? where ean=?"
            # self.cursor.execute(
            #     sql, (data, itens, total_compra, forma_pagamento, pago, troco))
            # self.conn.commit()

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
        # print(id)
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
        # print(termo)
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
            # print(linha[1])
            cancelado = linha[1]

        sql = "UPDATE vendas SET ativo='CANCELADO' WHERE coo=?"
        self.cursor.execute(sql, (coo,))
        self.conn.commit()
        afetado = self.cursor.rowcount
        if afetado > 0:
            return True, cancelado
        else:
            return False, False

    # imprime o cupom caso tenha o coo, se nao tiver imprime a reducao do dia
    def criaCupom(self, coo=False, login=False, reducaoz=False, saida=False, data=False, operador=False):

        if coo:  # se for cupom de venda ou cancelamento
            sql_busca = 'select * from vendas where coo=?'
            self.cursor.execute(
                sql_busca, (coo,))

            for linha in self.cursor.fetchall():
                # print(linha)
                coo = linha[0]
                ativo = linha[1]
                vdata = linha[2]
                itens = eval(linha[3])
                total = linha[4]
                forma = linha[5]
                pago = linha[6]
                troco = linha[7]

        elif reducaoz:  # se for reducao do dia
            cupom_ativo, cupom_cancelado = [], []
            sql_ativos = f'SELECT forma_pagamento,sum(valor_pago) from vendas where data like "{dataResumida}%" and ativo="SIM" GROUP by forma_pagamento'
            qtd_ativo = self.cursor.rowcount
            self.cursor.execute(sql_ativos)
            for i in self.cursor.fetchall():
                cupom_ativo.append(i)
            # print(cupom_ativo)
            sql_cancelados = f'SELECT forma_pagamento,sum(valor_pago) from vendas where data like "{dataResumida}%" and ativo="CANCELADO" GROUP by forma_pagamento'
            qtd_cancelado = self.cursor.rowcount
            self.cursor.execute(sql_cancelados)
            for i in self.cursor.fetchall():
                cupom_cancelado.append(i)
            # print(cupom_cancelado)
        elif saida:
            cupom_ativo, cupom_cancelado = [], []
            sql_ativos = f'SELECT forma_pagamento,sum(valor_pago) from vendas where data like "{data}%" and operador = "{operador}" and ativo="SIM" GROUP by forma_pagamento'
            qtd_ativo = self.cursor.rowcount
            self.cursor.execute(sql_ativos)
            for i in self.cursor.fetchall():
                cupom_ativo.append(i)
            print(cupom_ativo)
            sql_cancelados = f'SELECT forma_pagamento,sum(valor_pago) from vendas where data like "{data}%" and operador = "{operador}" and ativo="CANCELADO" GROUP by forma_pagamento'
            qtd_cancelado = self.cursor.rowcount
            self.cursor.execute(sql_cancelados)
            for i in self.cursor.fetchall():
                cupom_cancelado.append(i)
            print(cupom_cancelado)
        # prepara o cupom
        with open(f'CONFIG/cupom1.txt', 'r') as inicioCupom:
            inicioCupom = inicioCupom.readlines()

            with open(f'CONFIG/cupom2.txt', 'r') as fimCupom:
                fimCupom = fimCupom.readlines()

                with open(f'{nome_cupom}.txt', 'w') as e:

                    # escreve o inicio do cupom
                    for inicio in inicioCupom:
                        if coo:
                            e.write(inicio.replace('{coo}', str(coo)))
                        else:
                            e.write(inicio.replace(
                                'EXTRATO No. {coo}', ' FIM DO DIA'))

                    if coo:
                        # verifica se é cancelamento
                        if ativo == 'CANCELADO':
                            e.write(
                                f'Cupom No{coo} foi cancelado em {vdata}\n')

                            # retorna o estoque
                            for i in itens:
                                qtd = i[0]
                                cod = i[1]
                                # print(f'{qtd=} {cod=}')
                                # recebe o estoque atual do produto
                                sql = "SELECT * FROM produtos WHERE ean = ?"
                                # termo = f'%{termo}%'
                                self.cursor.execute(
                                    sql, (cod,))

                                for linha in self.cursor.fetchall():
                                    quantidade = linha[4]
                                # print(f'{quantidade=}')
                                qtd = int(quantidade)+int(qtd)
                                sql = "UPDATE produtos set quantidade=? where ean=?"
                                self.cursor.execute(sql, (qtd, cod))
                                self.conn.commit()
                        else:
                            # se for venda normal
                            for i in itens:
                                tot = float(i[3] / i[0])
                                valor = float(i[3])
                                # escreve os itens da compra
                                e.write(
                                    f'{i[1]} {i[2]}\n        {i[0]} X {"{:.2f}".format(tot)} = R${"{:.2f}".format(valor)}\n')

                    else:
                        # gera o fim do dia
                        txt_ativo = ''
                        txt_ativo += 'VENDAS EFETUADAS\n'

                        for i in cupom_ativo:
                            tipo, vtotal = i[0], i[1]
                            txt_ativo += f'\t{tipo} R${"{:.2f}".format(vtotal)}\n'

                        txt_cancelado = 'VENDAS CANCELADAS\n'
                        for i in cupom_cancelado:
                            tipo, vtotal = i[0], i[1]
                            txt_cancelado += f'\t{tipo} R${"{:.2f}".format(vtotal)}\n'

                        e.write(txt_ativo)
                        e.write('\n'+txt_cancelado)

                    # escreve o fim do cupom
                    if coo:
                        for fim in fimCupom:
                            e.write(fim.replace('{total}', str(total)).replace('{forma}', str(forma)).replace(
                                '{pago}', str(pago)).replace('{troco}', str(troco)).replace('{data}', str(vdata)))
                    else:
                        e.write(
                            f'\n\n\n\t{login}\n-----------------------------------------\n\t{str(data)}')

        try:
            import serial

            ser = serial.Serial(porta_com, 9600)
            with open(f'{nome_cupom}.txt', 'r') as f:
                text = f.read()

            ser.write(text.encode())

            return f'{nome_cupom}.txt'
        except:
            return False

    def saiOperador(self, data, operador):

        cupom_ativo, cupom_cancelado = [], []
        sql_ativos = f'SELECT forma_pagamento,sum(valor_pago) from vendas where data like "{data}%" and operador = "{operador}" and ativo="SIM" GROUP by forma_pagamento'
        qtd_ativo = self.cursor.rowcount
        self.cursor.execute(sql_ativos)
        for i in self.cursor.fetchall():
            cupom_ativo.append(i)
        print(cupom_ativo)
        sql_cancelados = f'SELECT forma_pagamento,sum(valor_pago) from vendas where data like "{data}%" and operador = "{operador}" and ativo="CANCELADO" GROUP by forma_pagamento'
        qtd_cancelado = self.cursor.rowcount
        self.cursor.execute(sql_cancelados)
        for i in self.cursor.fetchall():
            cupom_cancelado.append(i)
        print(cupom_cancelado)


if __name__ == "__main__":
    sistema = sys.platform
    if sistema == 'linux':
        operacoes = Operacoes('../DB/dbase.db')
        # acesso = Acesso('../DB/dbase.db')
        foto = '../img/tela.jpg'
    else:
        operacoes = Operacoes('..\\DB\\dbase.db')
        foto = '..\\img\\tela.jpg'

    operacoes.saiOperador('06-02-2023', '1980')
    # acesso = Acesso('..\\DB\\dbase.db')
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
    # retorno = operacoes.criaCupom(login='Christian Carvalho')
    # print(operacoes.reducaoZ())
    # print(retorno)
    # import serial

    # ser = serial.Serial('/dev/ttyACM0', 9600)
    # with open(f'CUPOM/cupom_7.txt', 'r') as f:
    #     text = f.read()
    # ser.write(text.encode())
