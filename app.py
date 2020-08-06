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
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import base64

#---     METODOS


#---     VARIABLES ESTATICAS     ---#
# Link Repositorio
LINK_GITHUB = 'https://github.com/psao/UVG-CC3066-P01-Limpieza-INE-Accidentes-Transito'

DESCRIPCION_PROYECTO = """
Se muestra una exploración básica de los datos promedios de los Accidentes de Transito, según la información 
obtenida desde la página del Instituto Nacional de Estadística de Guatemala.
"""
PATH_DATA_FILE = 'Accidentes de Transito.xlsx'

# Cargando información de Fallecidos y Lesionados

DATA_FALLECIDOS_LESIONADOS = pd.read_excel(PATH_DATA_FILE, sheet_name='Fallecidos-Lesionados')
FILTRO_ANIOS = DATA_FALLECIDOS_LESIONADOS.año_ocu.unique()
FILTRO_DEPARTAMENTOS = manager.getFiltroDepto(DATA_FALLECIDOS_LESIONADOS)


# Cargando información de Hechos de Transito
DATA_HECHOS_TRANSITO = pd.read_excel(PATH_DATA_FILE, sheet_name='Hechos-Transito')

# Cargando información de Vehículos involucrados
DATA_VEHICULOS_INVOLUCRADOS = pd.read_excel(PATH_DATA_FILE, sheet_name='Vehiculos-Involucrados')




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
                        html.H2(children='Exploración: Accidentes de Tránsito'),
                        html.P(children='Pablo Sao (Ing. Bioinformática)'),
                        html.P(children=DESCRIPCION_PROYECTO,id='texto-info')
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
                                                ],width={"size": 2},id='filter-anio'#,align="right"
                                                ),

                                                dbc.Col(children=[
                                                    dcc.RangeSlider(
                                                        id = 'sl-rango-anios',
                                                        min=min(FILTRO_ANIOS),
                                                        max=max(FILTRO_ANIOS),
                                                        # step=None,
                                                        marks=manager.getLabelFiltroAnios(FILTRO_ANIOS),
                                                        value=[min(FILTRO_ANIOS), max(FILTRO_ANIOS)]
                                                    ),
                                                ]), #,width={"size": 4,},align="right"),

                                                dbc.Col(children=[
                                                    html.H6("Departamentos")
                                                ],width={"size": 2},id='filter-departament'#,align="right"
                                                ),

                                                dbc.Col(children=[
                                                    dcc.Dropdown(
                                                        id = 'dropdown-deptos',
                                                        options=[
                                                            {'label': i[1]['depto_ocu'], 'value': i[1]['depto_ocu']} for i in FILTRO_DEPARTAMENTOS.iterrows()
                                                        ],
                                                        multi=True,
                                                        placeholder='Seleccione Departamentos'
                                                    ),
                                                ]),

                                            ],#,no_gutters=True,
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
    [dash.dependencies.Input('dropdown-deptos', 'value'),
     dash.dependencies.Input('sl-rango-anios', 'value')])
def update_output(dropdownDeptos,value):


    FiltroDepto = ''

    if( (dropdownDeptos is not None) and (len(dropdownDeptos)>0)):
        FiltroDepto = manager.getWhereIn('depto_ocu', dropdownDeptos)



    NombreDeptos = ''
    control_len = 70
    if(dropdownDeptos is not None and len(dropdownDeptos) > 0):
        NombreDeptos = ' <br> de '
        for valor in dropdownDeptos:
            NombreDeptos += ' {0},'.format(valor)
            if(len(NombreDeptos) >=control_len):
                control_len +=70
                NombreDeptos += ' <br> '

    # Llamado del promedio de lesionados y fallecidos
    avg_les_fall = manager.getLesionadoFallecido(DATA_FALLECIDOS_LESIONADOS, int(value[0]), int(value[1]),FiltroDepto)

    # obteniendo promedio de estado de conductores por sexo (hebrio, sobrio)
    avg_estado_conductor = manager.getEstadoConductor(DATA_VEHICULOS_INVOLUCRADOS,int(value[0]),int(value[1]))

    #
    #              Obtenemos la cantidad de casos por Color de vehículo
    # -------------------------------------------------------------------------
    avg_casos_color_vehiculo = manager.getCasosColor(DATA_VEHICULOS_INVOLUCRADOS,int(value[0]),int(value[1]),FiltroDepto)

    trace_colorVehiculo = go.Bar(x=avg_casos_color_vehiculo['color_veh'],
                                 y=avg_casos_color_vehiculo['cantidad'],
                                 text=avg_casos_color_vehiculo['cantidad'],
                                 textposition='auto'
                                )
    layout_color = go.Layout(title='Promedio de Accidentes del año {0} al {1}, <br>por Color de Vehículo {2}'.format(int(value[0]),int(value[1]),NombreDeptos),
                        # Same x and first y
                        xaxis_title='Color de Vehículo',
                        yaxis_title='Promedio de Accidentes',
                        height=700
                        )

    #
    #              Obtenemos la cantidad de casos por Tipo de Vehículo
    # -------------------------------------------------------------------------
    avg_casos_tipo_vehiculo = manager.getCasosTipoVehiculo(DATA_HECHOS_TRANSITO,int(value[0]),int(value[1]),FiltroDepto)

    trace_tipoVehiculo = go.Bar(x=avg_casos_tipo_vehiculo['tipo_veh'],
                                 y=avg_casos_tipo_vehiculo['cantidad'],
                                 text=avg_casos_tipo_vehiculo['cantidad'],
                                 textposition='auto'
                                 )
    layout_tipoV = go.Layout(
        title='Promedio de Accidentes del año {0} al {1}, <br>por Tipo de Vehículo {2}'.format(int(value[0]), int(value[1]),NombreDeptos),
        # Same x and first y
        xaxis_title='Tipo de Vehículo',
        yaxis_title='Promedio de Accidentes',
        height=700
        )

    #
    #              Obtenemos la cantidad de casos por Departamento
    # -------------------------------------------------------------------------
    avg_casos_municipio = manager.getFallecidosDepartamento(DATA_FALLECIDOS_LESIONADOS,int(value[0]),int(value[1]),FiltroDepto)

    trace_departamento = go.Bar(x=avg_casos_municipio['depto_ocu'],
                                y=avg_casos_municipio['cantidad'],
                                text=avg_casos_municipio['cantidad'],
                                textposition='auto'
                                )
    layout_departamento = go.Layout(
        title='Promedio de Accidentes del año {0} al {1}, <br>por Departamento'.format(int(value[0]), int(value[1])),
        # Same x and first y
        xaxis_title='Departamento',
        yaxis_title='Promedio de Accidentes',
        height=700
    )

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

        html.Br(),

        dbc.Row([
            dbc.Col(children=[

                dcc.Graph(id='graph-vcolor', figure={
                    'data': [trace_colorVehiculo],
                    'layout': layout_color
                }),
            ]),

            dbc.Col(children=[

                dcc.Graph(id='graph-vtipo', figure={
                    'data': [trace_tipoVehiculo],
                    'layout': layout_tipoV
                }),
            ]),
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col(children=[

                dcc.Graph(id='graph-depto', figure={
                    'data': [trace_departamento],
                    'layout': layout_departamento
                }),
            ]),
        ]),

    )

    #return 'You have selected "{}"'.format(avg_les_fall['hombre']['fallecidos'])


if __name__ == '__main__':
    app.run_server()