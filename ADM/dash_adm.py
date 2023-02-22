from dateutil.relativedelta import relativedelta
from dash import Dash, html, dcc, Input, Output
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

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
conn = sqlite3.connect('../DB/dbase.db')
categorias = ['produtos', 'vendas', 'usuarios']

# cria o dataframe de vendas
df = pd.read_sql_query("SELECT * FROM vendas ", conn)
df["total_compra"] = pd.to_numeric(df["total_compra"])
df['data'] = pd.to_datetime(df['data'], format="%d-%m-%Y %H:%M:%S")

# cria o grafico de vendas
fig = px.bar(df, x="data", y="total_compra", color="operador", barmode="group")
opcoes = list(df['operador'].unique())
opcoes.append('Todos')


# monta a pagina
app.layout = html.Div(children=[
    html.P(children='##### SiSVendas 2023 #####', style={
        'textAlign': 'center', 'fontSize': '30px', }),


    html.H2(id='assunto',
            children='Vendas por Operador/data em R$', style={'textAlign': 'center', }),

    html.Div(children=[
        html.Div(children=[
            html.P('Tipo de Grafico',
                   style={'display': 'inline-block', }),
            dcc.RadioItems(id='seletor_grafico', options=[
                'VENDIDO', 'CANCELADO', ], value='Vendas', style={'display': 'flex'}
            ),
        ], style={'display': 'inline-block',  'padding-right': 20, 'height': '90px',  'vertical-align': 'top'}),
        html.Div(children=[
            html.P(children='Selecione o período: '),
            dcc.DatePickerRange(
                id='date_filter',
                start_date=date(int(ano), int(mes), 1),
                end_date=date(int(ano), int(mes), int(ultimodia)),
                display_format='D-M-Y', style={}),
        ], style={'display': 'inline-block', 'height': '90px', }),
        html.Div(children=[
            html.P(children='Selecione o Operador: ',
                   ),
            dcc.Dropdown(opcoes, value='Todos',
                         id='dropdown_lista_operador', clearable=False),
        ], style={'display': 'inline-block',  'padding-left': 30, 'height': '90px', 'vertical-align': 'top'}),
        html.Br(),
        dcc.Graph(
            id='grafico_quantidade_vendas',
            style={'display': 'inline-block',
                   'width': '70%', 'textAlign': 'center'}
        ), dcc.Graph(
            id='grafico_quantidade_tipo',
            style={'display': 'inline-block',
                   'width': '30%', 'textAlign': 'center'}
        )
    ], style={'padding-bottom': 20, 'background-color': '#7B4831',  'vertical-align': 'top',  "textAlign": "center"}),
    html.Br(),
    html.Button('Filtrar', id='bt_enviar', n_clicks=0),


], style={'background-color': '#491A06', 'width': '90%', 'height': '100%',   "textAlign": "center", "border-style": "dotted"})


@ app.callback(
    Output('grafico_quantidade_vendas', 'figure'),
    Output('grafico_quantidade_tipo', 'figure'),
    Input('dropdown_lista_operador', 'value'),
    Input("date_filter", "start_date"),
    Input("date_filter", "end_date"),
    Input('seletor_grafico', 'value'),
    Input('bt_enviar', 'n_clicks'),

)
def update_output(value, start_date, end_date, tipo, botao):
    # print(f'{start_date=}, {end_date=}, {tipo=}, {botao=}')
    # start_date = pd.to_datetime(start_date) - timedelta(days=1)
    end_date = pd.to_datetime(end_date) + timedelta(days=1)
    print(f'{start_date=}, {end_date=}, {tipo=}, {value=}')
    ultimo = str(end_date)[:10]
    situacao = 'SIM'
    if tipo == 'VENDIDO':
        situacao = 'SIM'
    else:
        situacao = 'CANCELADO'

    # pesquisa por datas
    tabela_atualizada = df.loc[df["data"].between(pd.to_datetime(
        start_date), pd.to_datetime(end_date))]
    print(tabela_atualizada)
    if value == 'Todos':
        tabela_atualizada = tabela_atualizada.loc[(tabela_atualizada['ativo']
                                                   == situacao), :]
    else:
        tabela_atualizada = tabela_atualizada.loc[((tabela_atualizada['operador']
                                                    == value) & (tabela_atualizada['ativo']
                                                                 == situacao)), :]
    # modifica para data simples
    tabela_atualizada['data'] = tabela_atualizada['data'].dt.strftime(
        '%d-%m-%Y')
    # tabela_atualizada =tabela_atualizada.groupby("DIA")['CANCELADO'].sum()

    tabela_atualizada_vendas = tabela_atualizada.rename(
        columns={'total_compra': 'Venda por Dia em R$', 'data': 'Periodo'})
    fig = px.bar(tabela_atualizada_vendas, x="Periodo", y="Venda por Dia em R$", title=f'Vendas em R$ no Periodo de {start_date} á {ultimo}',
                 color="operador")

    tabela_atualizada_tipo = tabela_atualizada.rename(
        columns={'total_compra': 'Venda em R$', 'forma_pagamento': 'Tipo'})
    print(tabela_atualizada)
    fig1 = px.pie(tabela_atualizada_tipo,
                  values='Venda em R$',
                  names='Tipo',
                  title=f'Vendas por tipo de pagamento'
                  )

    return fig, fig1


if __name__ == '__main__':
    app.run_server(debug=True)
