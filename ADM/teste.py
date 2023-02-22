import sqlite3
from time import sleep
from datetime import datetime
import calendar
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference, BarChart
from openpyxl.styles import Font

conn = sqlite3.connect('..\\DB\\dbase.db')
categorias = ['produtos', 'vendas', 'usuarios']

# cria o dataframe de vendas
df = pd.read_sql_query("SELECT * FROM vendas where ativo = 'SIM'", conn)
df["total_compra"] = pd.to_numeric(df["total_compra"])
df['data'] = pd.to_datetime(df['data'], format="%d-%m-%Y %H:%M:%S")

# pesquisa por datas
tabela_atualizada = df.loc[df["data"].between(pd.to_datetime(
    '2023-02-07'), pd.to_datetime('2023-02-12'))]

# modifica para data simples
tabela_atualizada['data'] = tabela_atualizada['data'].dt.strftime('%d-%m-%Y')

tabela_atualizada = tabela_atualizada.loc[(tabela_atualizada['operador']
                                           == '1980'), :]
# agrupa por data e operador
# tabela_atualizada = tabela_atualizada.groupby(
#     ['data', 'operador'])['total_compra'].sum()

# tabela_atualizada['data'] = tabela_atualizada['data'].str[:10]

print(tabela_atualizada)
