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

DATA_HECHOS_TRANSITO = pd.read_excel(PATH_DATA_FILE, sheet_name='Hechos-Transito')

DATA_VEHICULOS_INVOLUCRADOS = pd.read_excel(PATH_DATA_FILE, sheet_name='Vehiculos-Involucrados')


print(manager.getCasosDepartamento(DATA_FALLECIDOS_LESIONADOS))

#####
q1 = """
        SELECT 
             tipo_eve as 'Tipo de Evento'
            ,año_ocu as 'Año Ocurrido'
        FROM 
            DATA_FALLECIDOS_LESIONADOS
      """

temp_fallecidos = psql.sqldf(q1, locals())

#print( psql.sqldf(q1, locals()) )


table = pd.pivot_table(temp_fallecidos,index=["Tipo de Evento"],columns=["Año Ocurrido"],values=["Año Ocurrido"],aggfunc={"Año Ocurrido":len},fill_value=0)

columnas_table = []
for columnas in list(table.columns):
    columnas_table.append(str(columnas[1]))

table.columns = columnas_table
table.insert(0, 'Tipo de Evento', table.index)


#for colum in list(table.max())[1:]:
#    print(colum)

"""
if 'id' in table:
    columnas_numericas = table.select_dtypes('number').drop(['id'], axis=1)
else:
    columnas_numericas = table.select_dtypes('number')

for (columnName, columnData) in columnas_numericas.iteritems():
    max_value = max(columnData)
    print(max_value)

print(columnas_numericas)
"""

#print(style_heatMap_table(table))
#print(list(table.columns[1:]))

#---     FIN VARIABLES ESTATICAS     ---#


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

#Layout de la pagina
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
                                            "El contenido se esconde al colapsarse el panel y ahorita se anda probando si funciona el size asignado de 10 y ver como queda el espacio")
                                    ),
                                    id="collapse",
                                ),
                            ]
                        )],
                    # width={"size": 10},
                ),

            ],
            justify="around",
        ),

        html.Br(),

        dbc.Row([
            dbc.Col(
                children=[
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": i, "id": i} for i in table.columns],
                        data=table.to_dict('records'),
                        style_data_conditional= manager.style_heatMap_table(table)
                        # [
                        #        {
                        #            'if': {
                        #                'filter_query': '{2017} > 1000', # comparing columns to each other
                        #               'column_id': '2017'
                        #            },
                        #            'backgroundColor': '#3D9970',
                        #            'color': 'white',
                        #        }
                        #    ]
                    ),
                ]),

        ]),

    ],fluid=True),

])

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-filtros", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server()