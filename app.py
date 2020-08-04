"""
Dashboard de Exploración
:author: Pablo Sao
:date: 14 de julio de 2020
"""
import manager
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
import pandas as pd
import pandasql as psql
import base64
import math

#---     METODOS


#---     VARIABLES ESTATICAS     ---#
# Link Repositorio
LINK_GITHUB = ''

PATH_DATA_FILE = 'Accidentes de Transito.xlsx'

DATA_FALLECIDOS_LESIONADOS = pd.read_excel(PATH_DATA_FILE, sheet_name='Fallecidos-Lesionados')
#print(manager.getLesionadoFallecido(DATA_FALLECIDOS_LESIONADOS,2017,2019))

FILTRO_ANIOS = DATA_FALLECIDOS_LESIONADOS.año_ocu.unique()

#DATA_HECHOS_TRANSITO = pd.read_excel(PATH_DATA_FILE, sheet_name='Hechos-Transito')


DATA_VEHICULOS_INVOLUCRADOS = pd.read_excel(PATH_DATA_FILE, sheet_name='Vehiculos-Involucrados')
#print(manager.getEstadoConductor(DATA_VEHICULOS_INVOLUCRADOS,2017,2019))





#q1 = """
#        SELECT
#             tipo_eve as 'Tipo de Evento'
#            ,año_ocu as 'Año Ocurrido'
#        FROM
#            DATA_FALLECIDOS_LESIONADOS
#      """

"""
temp_fallecidos = psql.sqldf(q1, locals())

#print( psql.sqldf(q1, locals()) )


table = pd.pivot_table(temp_fallecidos,index=["Tipo de Evento"],columns=["Año Ocurrido"],values=["Año Ocurrido"],aggfunc={"Año Ocurrido":len},fill_value=0)

columnas_table = []
for columnas in list(table.columns):
    columnas_table.append(str(columnas[1]))

table.columns = columnas_table
table.insert(0, 'Tipo de Evento', table.index)

print(manager.getCasosMunicipio(DATA_FALLECIDOS_LESIONADOS))

"""

# Logo universidad del Valle de Guatemala
file_uvg_logo = 'uvg-logo.jpg' # replace with your own image
UVG_LOGO = base64.b64encode(open(file_uvg_logo, 'rb').read())

# Creando aplicacion de Dash
app = dash.Dash(__name__,
    external_stylesheets=[dbc.themes.UNITED],
    external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',],
)

server = app.server

#Colocando titulo a la pestania
app.title = 'Accidentes de Transito'
app.layout = html.Div(children=[
    dbc.Container(children=[

        dbc.Row(
            [
                dbc.Col(
                    html.Img(src='data:image/png;base64,{}'.format(UVG_LOGO.decode()), style={'width': '125px'}),
                    width={"size": 2, "order": 1},
                ),
                dbc.Col(
                    (
                        html.Br(),
                        html.H2(children='Exploración: Accidentes de Transito'),
                        html.P(children='Pablo Sao'),
                    ),
                    width={"size": 6,"order": 2},
                ),
                dbc.Col(
                    (
                        html.Br(),
                        html.Br(),
                        html.A('Código en Github', href=LINK_GITHUB),
                    ),
                    width={"size": 3,"order": 3},
                ),
            ],
        ),

        html.Br(),

        dbc.Row(
            [
                dbc.Col(
                    children=[
                        html.Div(
                            [
                                dbc.Button(
                                    "Filtros",
                                    outline=True,
                                    id="collapse-filtros",
                                    className="mb-3",
                                    color="info",
                                ),
                                dbc.Collapse(
                                    dbc.Card(
                                        dbc.CardBody(
                                            dbc.Row([
                                                dbc.Col(children=[
                                                    html.H6("Rango de Años:")
                                                ],width={"size": 3,"offset": 2},align="left"),
                                                dbc.Col(children=[
                                                    dcc.RangeSlider(
                                                        id = 'sl-rango-anios',
                                                        min=min(FILTRO_ANIOS),
                                                        max=max(FILTRO_ANIOS),
                                                        # step=None,
                                                        marks=manager.getLabelFiltroAnios(FILTRO_ANIOS),
                                                        value=[min(FILTRO_ANIOS), max(FILTRO_ANIOS)]
                                                    ),
                                                ],width={"size": 4,},align="right"),
                                            ],no_gutters=True,
                                            ),


                                            #"El contenido se esconde al colapsarse el panel y ahorita se anda probando si funciona el size asignado de 10 y ver como queda el espacio"

                                        )
                                    ),
                                    id="collapse",
                                ),
                            ]
                        )
                    ],
                ),
            ],
            justify="around",
        ),

        html.Br(),

        html.Div(id='output-container-range-slider')

        #dbc.Row([
        #    dbc.Col(
        #        children=[
                    #dash_table.DataTable(
                    #    id='table',
                    #    columns=[{"name": i, "id": i} for i in table.columns],
                    #    data=table.to_dict('records'),
                    #    style_data_conditional= manager.style_heatMap_table(table)
                    #),

                    #html.Div([
                    #    dbc.Row([
                    #        #dbc.Col(children=[
                    #        #    html.H3("Descripción")
                    #        #],align="center"),
                    #        dbc.Col(children=[
                    #            html.H4("HOMBRES"),
                    #            html.Div(id='output-container-range-slider')
                    #        ],align="center"),
                    #        dbc.Col(children=[
                    #            html.H4("MUJERES")
                    #        ],align="center"),
                    #    ],align="center"
                    #    ),
                    #]),


        #        ]),

        #]),

    ],fluid=True),

])

# Evento para colapsar panel
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-filtros", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n,is_open):
    if is_open is None:
        is_open = True
        return is_open

    return not is_open

# Filtro de Slider
@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('sl-rango-anios', 'value')])
def update_output(value):


    # Llamado del promedio de lesionados y fallecidos
    avg_les_fall = manager.getLesionadoFallecido(DATA_FALLECIDOS_LESIONADOS, int(value[0]), int(value[1]))

    avg_estado_conductor = manager.getEstadoConductor(DATA_VEHICULOS_INVOLUCRADOS,int(value[0]),int(value[1]))

    return (

        dbc.Row([

            dbc.Col(children=[
                html.H3("Masculino",id="cart-custom")
            ],align="center"),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Fallecidos"),
                    dbc.CardBody(
                        [
                            html.H2(avg_les_fall['hombre']['fallecidos'],className="card-title"),
                        ],id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ],align="center"),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Lesionados",id="cart-custom"),
                    dbc.CardBody(
                        [
                            html.H2(avg_les_fall['hombre']['lesionados'], className="card-title"),
                        ],id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ]),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Bajo Efectos de Alcohol", id="cart-custom"),
                    dbc.CardBody(
                        [
                            html.H2(avg_estado_conductor['hombre']['Ebrios'], className="card-title"),
                        ], id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ]),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Sobrios",id="cart-custom"),
                    dbc.CardBody(
                        [
                            html.H2(avg_estado_conductor['hombre']['Sobrio'], className="card-title"),
                        ], id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ]),

        ]),

        html.Br(),

        dbc.Row([

            dbc.Col(children=[
                html.H3("Femenino", id="cart-custom")
            ], align="center"),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Fallecidas"),
                    dbc.CardBody(
                        [
                            html.H2(avg_les_fall['mujer']['fallecidos'], className="card-title"),
                        ], id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ], align="center"),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Lesionadas", id="cart-custom"),
                    dbc.CardBody(
                        [
                            html.H2(avg_les_fall['mujer']['lesionados'], className="card-title"),
                        ], id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ]),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Bajo Efectos de Alcohol", id="cart-custom"),
                    dbc.CardBody(
                        [
                            html.H2(avg_estado_conductor['mujer']['Ebrios'], className="card-title"),
                        ], id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ]),

            dbc.Col(children=[
                dbc.Card(children=[
                    dbc.CardHeader("Sobrias", id="cart-custom"),
                    dbc.CardBody(
                        [
                            html.H2(avg_estado_conductor['mujer']['Sobrio'], className="card-title"),
                        ], id="cart-custom"
                    ),
                ], color="info", inverse=True),
            ]),

        ]),

    )

    #return 'You have selected "{}"'.format(avg_les_fall['hombre']['fallecidos'])


if __name__ == '__main__':
    app.run_server()