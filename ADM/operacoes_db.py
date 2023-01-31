import sqlite3
from time import sleep
import os
import re
import sys

sistema = sys.platform
if sistema == 'linux':
    nome_cupom = 'CUPOM/cupom_'
else:
    nome_cupom = 'CUPOM\\cupom_'


class Operacoes:

    def __init__(self, arquivo):
        self.conn = sqlite3.connect(arquivo)
        self.cursor = self.conn.cursor()

    def cadastrarProduto(self, ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra, botao):
        # print(botao)
        try:
            if ativo == 'SIM':
                ativo = '1'
            else:
                ativo = '2'

            ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra = str(ativo).upper(), str(ean).upper(), str(
                produto).upper(), str(quantidade).upper(), str(valor_custo).upper().replace(',', '.'), str(valor_venda).upper().replace(',', '.'), str(ultima_compra).upper()

            rativo, rean, rproduto, rquantidade, rvalor_custo, rvalor_venda, rultima_compra = self.buscarProduto(
                termo=ean)

            if str(botao) == 'Cadastrar':
                if rean == ean:
                    return False
                else:

                    sql = "INSERT INTO produtos (ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra) VALUES (?,?,?,?,?,?,?)"
                    self.cursor.execute(
                        sql, (ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra))
                    self.conn.commit()
                    return True
            else:

                try:
                    sql = "UPDATE produtos SET ativo=?, produto=?, quantidade=?, valor_custo=?, valor_venda=? WHERE ean=?"
                    self.cursor.execute(sql, (ativo, produto, quantidade,
                                        valor_custo, valor_venda, ean))
                    self.conn.commit()
                    return True
                except Exception as e:
                    # print(e)
                    return False

        except Exception as e:
            # print(e)
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
        sql = "SELECT * FROM "+tabela+" order by produto"
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

    def cadastrarUsuario(self, ativo, login, senha, nome, cpf, funcao, botao):
        # print(botao)
        try:
            if ativo == 'SIM':
                ativo = '1'
            else:
                ativo = '2'

            ativo, login, senha, nome, cpf, funcao = str(ativo).upper(), login, senha, str(
                nome).upper(), str(cpf).upper(), str(funcao).upper()

            rativo, rlogin, rsenha, rnome, rcpf, rfuncao = self.buscarUsuario(
                termo=login)
            # print(botao)
            if str(botao) == 'Cadastrar':
                if rlogin == login or rcpf == cpf:
                    return False, False
                else:

                    sql = "INSERT INTO usuarios (ativo, login, senha, nome, cpf, funcao ) VALUES (?,?,?,?,?,?)"
                    self.cursor.execute(
                        sql, (ativo, login, senha, nome, cpf, funcao))
                    self.conn.commit()
                    return True, 'cadastrado'
            else:

                try:
                    sql = "UPDATE usuarios SET ativo=?, login=?, senha=?, nome=?, cpf=?,funcao=? WHERE login=?"
                    self.cursor.execute(
                        sql, (ativo, login, senha, nome, cpf, funcao, login))
                    self.conn.commit()
                    return True, 'atualizado'
                except Exception as e:
                    return False, False

        except Exception as e:
            # print(e)
            return False

    def editarUsuario(self, id, ativo, login, senha, nome, cpf, funcao):
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

    def listar_tudoUsuario(self, tabela):
        itens = []
        sql = "SELECT * FROM "+tabela+" order by nome"
        self.cursor.execute(sql)
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        return itens

    def buscarUsuario(self, termo):
        # print(termo)
        try:
            contador = 0
            sql = "SELECT * FROM usuarios where login = ?"
            # termo = f'%{termo}%'
            self.cursor.execute(
                sql, (termo,))

            for linha in self.cursor.fetchall():

                contador += 1

                ativo = linha[0]
                login = linha[1]
                senha = linha[2]
                nome = linha[3]
                cpf = linha[4]
                funcao = linha[5]

            return ativo, login, senha, nome, cpf, funcao
        except Exception as e:
            return '', '', '', '', '', ''


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
    retorno = operacoes.criaCupom('7')
    # retorno = operacoes.buscarUsuario('1980')
    print(retorno)
