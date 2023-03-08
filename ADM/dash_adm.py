from dateutil.relativedelta import relativedelta
from dash import Dash, html, dcc, Input, Output
import dash_table
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import date
from datetime import *

data_e_hora_atuais = datetime.now()
data_atual = date.today()
data = data_e_hora_atuais.strftime('%d-%m-%Y %H:%M:%S')
mes = data_e_hora_atuais.strftime('%m')
ano = data_e_hora_atuais.strftime('%Y')

ultimodia = str(date(int(ano), int(mes), 1) +
                relativedelta(day=31)).split('-')[2]


app = Dash(__name__)

try:
    conn = sqlite3.connect('../DB/dbase.db')
except:
    conn = sqlite3.connect('DB/dbase.db')
categorias = ['produtos', 'vendas', 'usuarios']

# cria o dataframe de vendas
df = pd.read_sql_query("SELECT * FROM vendas ", conn)


# # # # cria o grafico de vendas
# fig = px.bar(df, x="data", y="total_compra",
#              color="operador", barmode="group")
# opcoes = list(df['operador'].unique())
# opcoes.append('Todos')


# monta a pagina
app.layout = html.Div(children=[
    dcc.Interval(
        id='interval-component',
        interval=2*60*1000,  # atualiza a cada 2 minutos
        n_intervals=0
    ),

    html.P(children='##### SiSVendas 2023 #####', style={
        'textAlign': 'center', 'fontSize': '30px', }),


    html.H2(id='assunto',
            children='Vendas por Operador/data em R$', style={'textAlign': 'center', }),

    html.Div(children=[
        # tipo de grafico
        html.Div(children=[
            html.P('Tipo de Grafico',
                   style={'display': 'inline-block', }),
            dcc.Dropdown(['VENDIDO', 'CANCELADO', 'MAIS VENDIDOS', 'RANKING OP'], value='VENDIDO',
                         id='seletor_grafico', clearable=False),
        ], style={'display': 'inline-block',  'padding': 10, 'width': '150px', 'height': '90px', 'vertical-align': 'top'}),
        # periodo
        html.Div(children=[
            html.P(children='Selecione o período: '),
            dcc.DatePickerRange(
                id='date_filter',
                start_date=date(int(ano), int(mes)-2, 1),
                end_date=date(int(ano), int(mes), int(ultimodia)),
                display_format='D-M-Y', style={}),
        ], style={'display': 'inline-block', 'height': '90px', 'vertical-align': 'top'}),
        # operador
        html.Div(children=[
            html.P(children='Selecione o Operador: ',
                   ),
            dcc.Dropdown(options=[{'label': caixa, 'value': caixa} for caixa in df['operador'].unique()]+[{'label': 'Todos', 'value': 'Todos'}],
                         value='Todos',
                         id='dropdown_lista_operador', clearable=False),
        ], style={'display': 'inline-block',  'padding': 10,  'height': '90px', 'vertical-align': 'top'}),
        # grafico de vendas e forma de pagto
        html.Div(children=[
            dcc.Graph(
                id='grafico_quantidade_vendas',
                style={'display': 'inline-block',
                       'width': '60%', 'textAlign': 'center'},
                config={'displayModeBar': False, },

            ), dcc.Graph(
                id='grafico_quantidade_tipo',
                style={'display': 'inline-block',
                       'width': '40%', 'textAlign': 'center'},
                config={'displayModeBar': False}
            )], style={'padding': 30, 'background-color': '#49aaff'})
    ], style={'padding-bottom': 20, 'background-color': '#ffffff', 'vertical-align': 'top',  "textAlign": "center"}),
    html.Div(children=[
        dcc.Graph(
            id='grafico_quantidade',
            style={'display': 'inline-block',
                   'width': '60%', 'textAlign': 'center'},
            config={'displayModeBar': False}
        )
    ])


], style={'background-color': '#49aaff', 'width': '90%', 'height': '100%',   "textAlign": "center", "border-style": "dotted"})


@ app.callback(
    Output('grafico_quantidade_vendas', 'figure'),
    Output('grafico_quantidade_tipo', 'figure'),
    Output('grafico_quantidade', 'figure'),
    [
        Input('dropdown_lista_operador', 'value'),
        Input("date_filter", "start_date"),
        Input("date_filter", "end_date"),
        Input('seletor_grafico', 'value'),
        Input('interval-component', 'n_intervals')
    ]

)
def update_output(value, start_date, end_date, tipo, n):
    '''
    cria o dataframe para a pagina
    '''
    try:
        conn = sqlite3.connect('../DB/dbase.db')
    except:
        conn = sqlite3.connect('DB/dbase.db')
    categorias = ['produtos', 'vendas', 'usuarios']

    # cria o dataframe de vendas
    df = pd.read_sql_query("SELECT * FROM vendas ", conn)
    df["total_compra"] = pd.to_numeric(df["total_compra"])
    df['data'] = pd.to_datetime(df['data'], format="%d-%m-%Y %H:%M:%S")

    start_date = pd.to_datetime(start_date) - timedelta(days=1)
    end_date = pd.to_datetime(end_date) + timedelta(days=1)
    ultimo = str(end_date)[:10]

    # pesquisa por datas
    tabela_atualizada = df.loc[df["data"].between(pd.to_datetime(
        start_date), pd.to_datetime(end_date))]

    if tipo == 'VENDIDO' or tipo == 'CANCELADO':
        if tipo == 'VENDIDO':
            situacao = 'SIM'
        elif tipo == 'CANCELADO':
            situacao = 'CANCELADO'

        if value == 'Todos':
            tabela_atualizada = tabela_atualizada.loc[(tabela_atualizada['ativo']
                                                       == situacao), :]
        else:
            tabela_atualizada = tabela_atualizada.loc[((tabela_atualizada['operador']
                                                      == value) & (tabela_atualizada['ativo']
                                                                   == situacao)), :]

        # modifica para data simples
        tabela_atualizada['data'] = tabela_atualizada['data'].dt.strftime(
            '%d/%m/%Y')

        tabela_atualizada_vendas = tabela_atualizada.rename(
            columns={'total_compra': 'Venda por Dia em R$', 'data': 'Periodo'})

        print(tabela_atualizada_vendas.info(), tabela_atualizada_vendas)

        fig = px.bar(tabela_atualizada_vendas, x="Periodo", y="Venda por Dia em R$", title=f'Vendas em R$ no Periodo de {start_date} á {ultimo}',
                     color="operador",)

        fig.update_layout(title=dict(
            xanchor='center',
            x=0.5
        ),
            legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5
        ))

        tabela_atualizada_tipo = tabela_atualizada.rename(
            columns={'total_compra': 'Venda em R$', 'forma_pagamento': 'Tipo'})

        grafico_pizza = px.pie(tabela_atualizada_tipo,
                               values='Venda em R$',
                               names='Tipo',
                               title=f'Vendas por tipo de pagamento'
                               )
        grafico_pizza.update_layout(title=dict(
            xanchor='center',
            x=0.5
        ), legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5
        ))

        # cria os dados de itens mais vendidos
        tabela_atualizada = tabela_atualizada.loc[(tabela_atualizada['ativo']
                                                   == 'SIM'), :]
        lista = tabela_atualizada['itens'].tolist()
        # Cria o dicionário para armazenar os dados de vendas de cada produto
        vendas_produtos = {}
        # Percorre as linhas do arquivo
        for linha in lista:
            # Converte a linha em uma lista de tuplas contendo os dados de vendas de cada produto
            dados_vendas = eval(linha.strip())

            # Percorre cada tupla da lista
            for quantidade, codigo, produto, valor in dados_vendas:
                # Verifica se o produto já existe no dicionário
                if produto in vendas_produtos:
                    # Adiciona a quantidade da tupla atual ao valor existente
                    vendas_produtos[produto] += quantidade
                else:
                    # Adiciona o produto como chave e a quantidade como valor
                    vendas_produtos[produto] = quantidade

        # Cria uma lista de tuplas contendo o produto e a quantidade total vendida
        lista_vendas = [(produto, quantidade)
                        for produto, quantidade in vendas_produtos.items()]

        # Classifica a lista em ordem alfabética pelo produto
        lista_vendas = sorted(lista_vendas, key=lambda x: x[0])

        tabela = []
        with open('teste.txt', 'w') as f:
            for produto, quantidade in lista_vendas:
                tabela.append({'Produto': produto, 'Quantidade': quantidade})
            f.write(str(tabela))

        return fig, grafico_pizza, grafico_maisvendido


if __name__ == '__main__':
    app.run_server(debug=True)
