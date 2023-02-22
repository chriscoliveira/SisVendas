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
conn = sqlite3.connect('..\\DB\\dbase.db')
categorias = ['produtos', 'vendas', 'usuarios']

# cria o dataframe de vendas
df = pd.read_sql_query("SELECT * FROM vendas where ativo = 'SIM'", conn)
df["total_compra"] = pd.to_numeric(df["total_compra"])
df['data'] = pd.to_datetime(df['data'], format="%d-%m-%Y %H:%M:%S")

# cria o grafico de vendas
fig = px.bar(df, x="data", y="total_compra", color="operador", barmode="group")
opcoes = list(df['operador'].unique())
opcoes.append('Todos')


# monta a pagina
app.layout = html.Div(children=[
    html.P(children='##### SiSVendas 2023 #####', style={
        'textAlign': 'center', 'fontSize': '60px', 'color': '#7FDBFF'}),


    html.H2(id='assunto',
            children='Vendas por Operador/data em R$', style={'textAlign': 'center', 'color': '#7FDBFF'}),

    html.Div(children=[
        html.H2('Tipo de Grafico',
                style={'display': 'inline-block', 'fontSize': '24px'}),
        dcc.RadioItems(id='seletor_grafico', options=[
            'Vendas', 'Forma Pagamento', ], value='Vendas',
            style={'display': 'inline-block', 'fontSize': '24px', 'padding': 10, 'flex': 1}),
        html.Br(),
        html.H2(children='Selecione o período: ',
                style={'display': 'inline-block', 'fontSize': '24px'}),
        dcc.DatePickerRange(
            id='date_filter',
            start_date=date(int(ano), int(mes), 1),
            end_date=date(int(ano), int(mes), int(ultimodia)),
            display_format='D-M-Y', style={'vertical-align': 'top'}),
        html.Br(),
        html.H2(children='Selecione o Operador: ',
                style={'display': 'inline-block', 'fontSize': '24px'}),
        dcc.Dropdown(opcoes, value='Todos', id='dropdown_lista_operador', style={
            'display': 'inline-block', 'width': '300px', 'height': '42px',  'fontSize': '24px'}),

    ], style={'textAlign': 'center', }),

    html.Button('Filtrar', id='bt_enviar', n_clicks=0),
    dcc.Graph(
        id='grafico_quantidade_vendas',
        figure=fig,
        responsive=True,
        animate=True,
        style={'width': '900px', }
    ),

], style={'background-color': '#7FDBFF'})


@ app.callback(
    Output('grafico_quantidade_vendas', 'figure'),
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
    print(f'{start_date=}, {end_date=}')

    if tipo == 'Vendas':
        if value == "Todos":
            # pesquisa por datas
            tabela_atualizada = df.loc[df["data"].between(pd.to_datetime(
                start_date), pd.to_datetime(end_date))]
            tabela_atualizada = tabela_atualizada.loc[(tabela_atualizada['ativo']
                                                       == 'SIM'), :]
            # modifica para data simples
            tabela_atualizada['data'] = tabela_atualizada['data'].dt.strftime(
                '%d-%m-%Y')
            # print(tabela_atualizada.info())

            fig = px.bar(tabela_atualizada, x="data", y="total_compra",
                         color="operador", barmode="group")

        else:
            # pesquisa por datas
            tabela_atualizada = df.loc[df["data"].between(pd.to_datetime(
                start_date), pd.to_datetime(end_date))]

            # modifica para data simples
            tabela_atualizada['data'] = tabela_atualizada['data'].dt.strftime(
                '%d-%m-%Y')

            # filtra por operador
            tabela_atualizada = tabela_atualizada.loc[((tabela_atualizada['operador']
                                                      == value) & (tabela_atualizada['ativo']
                                                                   == 'SIM')), :]
            print(tabela_atualizada)
            # print(tabela_atualizada)
            fig = px.bar(tabela_atualizada, x="data", y="total_compra",
                         color="operador", barmode="group")

    elif tipo == 'Forma Pagamento':
        # if value == "Todos":
        tabela_atualizada = df.loc[df["data"].between(pd.to_datetime(
            start_date), pd.to_datetime(end_date))]
        tabela_atualizada = tabela_atualizada.loc[(tabela_atualizada['ativo']
                                                   == 'SIM'), :]
        tabela_atualizada['data'] = tabela_atualizada['data'].dt.strftime(
            '%d-%m-%Y')
        print(tabela_atualizada)
        print(f'{start_date=}, {end_date=}, {tipo=}, {botao=}')
        fig = px.pie(tabela_atualizada,
                     values='total_compra',
                     names='forma_pagamento',
                     hole=.3,)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
