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
        print(botao)
        try:
            if ativo == 'SIM':
                ativo = '1'
            else:
                ativo = '2'
            ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra = str(ativo).upper(), str(ean).upper(), str(
                produto).upper(), str(quantidade).upper(), str(valor_custo).upper().replace(',', '.'), str(valor_venda).upper().replace(',', '.'), str(ultima_compra).upper()

            rativo, rean, rproduto, rquantidade, rvalor_custo, rvalor_venda, rultima_compra = self.buscarProduto(
                termo=ean)
            print(f'_{rean}_')
            if botao == 'Cadastrar':
                if rean == ean:
                    return False
                else:

                    sql = "INSERT INTO produtos (ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra) VALUES (?,?,?,?,?,?,?)"
                    self.cursor.execute(
                        sql, (ativo, ean, produto, quantidade, valor_custo, valor_venda, ultima_compra))
                    self.conn.commit()
                    return True
            else:
                print('atualizar')

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
        sql = "SELECT * FROM "+tabela
        self.cursor.execute(sql)
        contador = 0
        for linha in self.cursor.fetchall():
            contador += 1
            itens.append(linha)
        return itens

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
        with open(f'CONFIG\\cupom1.txt', 'r') as inicioCupom:
            inicioCupom = inicioCupom.readlines()

            with open(f'CONFIG\\cupom2.txt', 'r') as fimCupom:
                fimCupom = fimCupom.readlines()

                with open(f'{nome_cupom}{coo}.txt', 'w') as e:

                    # escreve o inicio do cupom
                    for inicio in inicioCupom:
                        e.write(inicio.replace('{coo}', str(coo)))

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
        return f'{nome_cupom}{coo}.txt'


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
    # retorno = operacoes.criaCupom('2')
    retorno = operacoes.listar_tudo('produtos')
    print(retorno)
