
import math
import pandas as pd
import pandasql as psql

def getLabelFiltroAnios(anios):

    LABEL_FILTRO_ANIOS = {}

    for valores in anios:
        LABEL_FILTRO_ANIOS.update({int(valores): {'label': str(valores)}})


    return LABEL_FILTRO_ANIOS


def getWhere(filtro):
    Where = ''

    for valor in range(len(filtro)):
        if(valor == 0):
            Where += filtro[valor]
        Where += ' AND {0}'.format(filtro[valor])

    return Where

def getCasosMunicipio(dataframe):
    q1 = """
            SELECT 
                 mupio_ocu as Municipio
                ,coordenada as Coordenada
                ,count(coordenada) as Cantidad
            FROM 
                dataframe
            WHERE
                coordenada <> '[]'
            group by mupio_ocu,coordenada
          """

    coordenadas = psql.sqldf(q1, locals())

    print(coordenadas)

def getLesionadoFallecido(dataframe,anio_inicial,anio_final):

    resultado = {}

    consulta = """
                SELECT
                     sexo_per
                    ,fall_les
                    ,round(avg(cantidad)) as cantidad
                FROM(
                        SELECT
                             sexo_per
                            ,fall_les
                            ,año_ocu
                            ,count(año_ocu) as cantidad
                        FROM
                            dataframe
                        where
                            año_ocu between {0} and {1} 
                        and fall_les is not null
                        and sexo_per <> '9 - Ignorado'
                        group by
                            sexo_per, fall_les,año_ocu
                    )
                group by sexo_per, fall_les
                order by sexo_per
               """.format(anio_inicial,anio_final)

    datos = psql.sqldf(consulta, locals())
    #print(datos)

    resultado = {'hombre':{
                            'fallecidos':int(datos['cantidad'].values[0]),
                            'lesionados':int(datos['cantidad'].values[1])
                          },
                 'mujer':{
                     'fallecidos': int(datos['cantidad'].values[2]),
                     'lesionados': int(datos['cantidad'].values[3])
                        },

                 }

    #print(datos['cantidad'].values[0])


    return resultado


def getEstadoConductor(dataframe, anio_inicial, anio_final):
    resultado = {}

    consulta = """
                SELECT
                     sexo_per
                    ,estado_con
                    ,round(avg(cantidad)) as cantidad
                FROM(
                        SELECT
                             sexo_per
                            ,estado_con
                            ,año_ocu
                            ,count(año_ocu) as cantidad
                        FROM
                            dataframe
                        where
                            año_ocu between {0} and {1} 
                        and estado_con is not null
                        and sexo_per <> '9 - Ignorado'
                        and estado_con <> '9 - Ignorado'
                        group by
                            sexo_per, estado_con,año_ocu
                    )
                group by sexo_per, estado_con
                order by sexo_per
               """.format(anio_inicial, anio_final)

    datos = psql.sqldf(consulta, locals())
    #print(datos)

    resultado = {'hombre': {
        'Ebrios': int(datos['cantidad'].values[1]),
        'Sobrio': int(datos['cantidad'].values[0])
    },
        'mujer': {
            'Ebrios': int(datos['cantidad'].values[3]),
            'Sobrio': int(datos['cantidad'].values[2])
        },

    }

    #print(datos['cantidad'].values[0])

    return resultado

def style_heatMap_table(dataframe):
    """
    Devuelve el estilo para elaborar un heatmap de una tabla
    :param dataframe: pandas DataFrame
    :return: json con el estilo de tabla
    """
    size_heatmap = 10

    if 'id' in dataframe:
        columnas_numericas = dataframe.select_dtypes('number').drop(['id'], axis=1)
    else:
        columnas_numericas = dataframe.select_dtypes('number')

    styles = []

    value = math.floor( (max(list(columnas_numericas.max()))) / size_heatmap)

    for (columnName, columnData) in columnas_numericas.iteritems():

        total = 0

        for rangos in range(size_heatmap):

            total += value

            color = ''
            color_letra = 'white'
            query = '{0} >= {1}'.format("{"+columnName+"}",total)

            if (rangos == 0):
                color = '#eff5fa'
                color_letra = 'black'
                query = '{0} <= {1}'.format("{" + columnName + "}",total)

            elif (rangos == 1):
                color = '#dbe8f5'
                color_letra = 'black'
            elif (rangos == 2):
                color = '#c3daef'
                color_letra = 'black'
            elif (rangos == 3):
                color = '#afceea'
            elif (rangos == 4):
                color = '#9bc2e5'
            elif (rangos == 5):
                color = '#87b6e0'
            elif (rangos == 6):
                color = '#73aadb'
            elif (rangos == 7):
                color = '#5f9ed6'
            elif (rangos == 8):
                color = '#3685cc'
            elif (rangos == 9):
                color = '#2b6aa3'

            styles.append(

                {
                    'if': {
                        'filter_query': query,  # comparing columns to each other
                        'column_id': '{0}'.format(columnName)
                    },
                    'backgroundColor': color,
                    'color': color_letra,
                }

            )

    return styles
