import sqlite3
from time import sleep
import os
import re


class Operacoes:

    def __init__(self, arquivo):
        self.conn = sqlite3.connect(arquivo)
        self.cursor = self.conn.cursor()

    def inserir(self, ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra):
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

    def remover(self, id):
        sql = "DELETE FROM produtos WHERE id=?"
        self.cursor.execute(sql, (id,))
        self.conn.commit()
        afetado = self.cursor.rowcount
        if afetado > 0:
            return f"O excluido com sucesso!"
        else:
            return f"Nenhum registro excluido"

    def listar_tudo(self):
        itens = []
        sql = "SELECT * FROM produtos"
        self.cursor.execute(sql)
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        return contador, itens

    def buscar(self, termo):
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


if __name__ == "__main__":
    operacoes = Operacoes("DB\\dbase.db")
    # retorno = operacoes.inserir(
    #     "1", "7891234", 'acucar', '10', '1,00', '4,50', '')
    # print(retorno)

    # retorno = operacoes.editar(
    #     '5', '0', '123', 'cafe', '12', '8,00', '13,01', '')
    # retorno = operacoes.remover('7')
    # print(retorno)

    # retorno = operacoes.listar_tudo()
    # print(retorno)

    # retorno = operacoes.buscar('789123')
    # print(retorno)
