
import math
import pandas as pd
import pandasql as psql
from geopy.geocoders import Nominatim

def getCoordenadas(direccion):
    #print(direccion)
    #address = 'Ciudad de Guatemala, Guatemala'
    try:
        print('Dentro del try')
        geolocator = Nominatim(user_agent="Pablo")
        location = geolocator.geocode(direccion)
        return [location.latitude, location.longitude]
    except:
        print('dentro del except')
        print(direccion)
        return list()



def getCasosDepartamento(DataFrame):

    paises = """
            SELECT 
                 depto_ocu as 'Departamento'
                ,mupio_ocu as 'Municipio'
                ,count(mupio_ocu) as 'Accidentes'
            FROM 
                DataFrame
            GROUP BY
                depto_ocu, mupio_ocu
          """

    coordenadas = psql.sqldf(paises, locals())

    coordenadas['coordenadas'] = coordenadas.apply(lambda row: getCoordenadas('{0},{1}, Guatemala'.format(
                                                                     row['Municipio'].split('-')[1]  # .replace(" ", "")
                                                                    ,row['Departamento'].split('-')[1]  # .replace(" ", "")
                                                                  )
                                                                )
                                                    , axis=1)

    return coordenadas


def style_heatMap_table(dataframe):
    size_heatmap = 5

    if 'id' in dataframe:
        columnas_numericas = dataframe.select_dtypes('number').drop(['id'], axis=1)
    else:
        columnas_numericas = dataframe.select_dtypes('number')

    styles = []

    value = 0

    for (columnName, columnData) in columnas_numericas.iteritems():
        if(value==0):
            value = math.floor(max(columnData) / size_heatmap)

        total = 0

        for rangos in range(size_heatmap):

            color = ''
            total += value
            if (rangos == 0):
                color = '#d7e6f4'
            elif (rangos == 1):
                color = '#afcdea'
            elif (rangos == 2):
                color = '#88b4e0'
            elif (rangos == 3):
                color = '#609bd6'
            elif (rangos == 4):
                color = '#3983cc'

            styles.append(

                {
                    'if': {
                        'filter_query': '{0} >= {1}'.format("{"+columnName+"}", total),  # comparing columns to each other
                        'column_id': '{0}'.format(columnName)
                    },
                    'backgroundColor': color,
                    'color': 'white',
                }

            )

    return styles
