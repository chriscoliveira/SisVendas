import sqlite3
from time import sleep
import os
import re


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

    def adicionaItem(self, ean, produto, valor):
        try:
            sql = "INSERT INTO venda_tmp (ean, produto,valor) VALUES (?,?,?)"
            self.cursor.execute(
                sql, (ean, produto, valor))
            self.conn.commit()
            return f"O {produto=} {ean=} foi adicionado!"
        except Exception as e:
            return f"Ocorreu um erro ao adicionar = {e}"

    def cadastrarVenda(self, data, itens, total_compra, forma_pagamento, pago,troco):
        try:
            sql = "INSERT INTO vendas (data, itens,total_compra,forma_pagamento,valor_pago,troco) VALUES (?,?,?,?,?,?)"
            self.cursor.execute(
                sql, (data, itens, total_compra, forma_pagamento, pago,troco))
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

    def remover_todos_produtos(self, tabela, id):
        sql = "DELETE FROM "+tabela+" WHERE id=?"
        self.cursor.execute(sql, (id,))
        self.conn.commit()
        afetado = self.cursor.rowcount
        if afetado > 0:
            return f"O excluido com sucesso!"
        else:
            return f"Nenhum registro excluido"

    def listar_tudo(self, tabela):
        itens = []
        sql = "SELECT ean,produto,valor FROM "+tabela
        self.cursor.execute(sql)
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        return itens

    def listar_itens_tmp(self,ean):
        itens = []
        sql = "SELECT id,ean,produto,valor FROM venda_tmp where ean = ?"
        self.cursor.execute(sql,(ean,))
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        
        id = 0
        for i in itens:
            id = i[0]
        
        retorno = self.remover_todos_produtos('venda_tmp',id)
        

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


if __name__ == "__main__":
    operacoes = Operacoes("DB/dbase.db")

    # retorno = operacoes.inserir(
    #     "1", "7891234", 'acucar', '10', '1,00', '4,50', '')
    # print(retorno)

    # retorno = operacoes.editar(
    #     '5', '0', '123', 'cafe', '12', '8,00', '13,01', '')
    # retorno = operacoes.remover('7')
    # print(retorno)

    # retorno = operacoes.listar_tudo(tabela='venda_tmp')
    # retorno = operacoes.agrupaItensTmp()
    # print(retorno)

    # retorno = operacoes.buscar('789123')
    retorno = operacoes.listar_itens_tmp('789')
    # retorno = operacoes.cadastrarVenda(
    #     '20-01-2023', 'aaaaaa', '50', 'dinheiro', '25')
    print(retorno)
