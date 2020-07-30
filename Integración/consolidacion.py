"""
Proceso para realizar la consolidación de los datos de accidentes de la INE
:author: Pablo Sao
:date: 13 de julio de 2020
"""
from os import listdir,remove
from os.path import isfile, join,exists
import pandas as pd
import pandasql as psql
from geopy.geocoders import Nominatim


def getNombreArchivos(path_file):
    """
    Método para obtener el nombre de todos los archivos del directorio
    :param path_file: String con la ruta del directorio
    :return: Array con el nombre de los archivos, si el directorio no existe, retorna un array vacío
    """
    archivos = []

    if(exists(path_file)):
        archivos = [f for f in listdir(path_file) if isfile(join(path_file, f))]

    return archivos

def relacionaCoordenadas(Dataframe, Departamento, Municipio):
    for i in range(len(Dataframe)):
        if(Dataframe.loc[i, "Departamento"] == Departamento and Dataframe.loc[i, "Municipio"] == Municipio):
            return Dataframe.loc[i, "coordenadas"]
            #print(Dataframe.loc[i, "Departamento"], Dataframe.loc[i, "Municipio"])

    return ""

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



def getData(path_archivos):
    """
    Método para obtener dataframe de todos los archivos de Excel contenidos en un directorio y colocar los valores de
    los catalogos en lugar de su codigo. El Excel debe tener la mismas columnas y la pestaña tener el nombre de
    "Sheet1".
    :param path_archivos: String con la ruta del directorio que contiene los Excel
    :return: DataFrame de Pandas. Retorna vacio si no hay archivos.
    """

    # Creamos DataFrame vacío
    tem_dataframe = pd.DataFrame()

    # Se obtienen todos los archivos contenidos en el path provisionado
    array_archivos = getNombreArchivos(path_archivos)

    # Verificamos si hay archivos en el directorio
    # si en dado caso no hay archivos, retorna el dataframe vacío
    if(len(array_archivos) > 0):

        for file in array_archivos:
            path_file = path_archivos + file

            # Verificamos si el archivo existe
            if (exists(path_file)):
                # Si existe el archivo, cargamos el archivo de Excel al DataFrame temporal
                tem_dataframe = pd.concat([tem_dataframe, pd.read_excel(path_file, sheet_name=0)], ignore_index=True)

        ## Remplazando códigos con valores
        for (columnName, columnData) in tem_dataframe.iteritems():

            # Revisando si la columna esta en un catalogo
            if(str(columnName) in CATALOGOS):

                # Abriendo Excel de catalogos
                temp_catalogo = pd.read_excel(PATH_CATALOGOS, columnName)

                # Concatenando el codigo con el valor para ser remplazado en la descripción
                temp_catalogo['valor'] = temp_catalogo.agg('{0[codigo]} - {0[valor]}'.format, axis=1)

                # Creamos columna con la descripcion del archivo de catalogos.
                tem_dataframe[columnName] = tem_dataframe[columnName].map(temp_catalogo.set_index('codigo')['valor'])

                #indexNames = tem_dataframe[(tem_dataframe[columnName].str[-10:] == '9999999999')].index
                #tem_dataframe.drop(indexNames, inplace=True)

    return tem_dataframe

def exportExcel(dataframe_list, sheet_name_list, file_name):

    # Creando Excel donde se guardara la información de los dataset
    writer = pd.ExcelWriter(file_name,engine='xlsxwriter')

    # Recorremos el listado de dataset a almacenar en el Excel
    for dataframe, sheet in zip(dataframe_list, sheet_name_list):
        # Se exporta en la pestaña con el nombre de la pestaña en la lista
        dataframe.to_excel(writer, sheet_name=sheet, index=False, startrow=0 , startcol=0)

    #Guardando documento
    writer.save()


## Variables Estaticas
PATH_CATALOGOS = '../Datos/00 - Diccionarios/Catalogos.xlsx'
CATALOGOS = pd.ExcelFile(PATH_CATALOGOS).sheet_names
#print(CATALOGOS)  # see all sheet names

########################

output_path = '../Accidentes de Transito.xlsx'

if(exists(output_path)):
    remove(output_path)


###########
print("Transformando Fallecidos y Lesionados...")
data_fallecidos = getData('../Datos/01 - Fallecidos y Lesionados/')

print("Obteniendo coordenadas y cantidad de Fallecidos por municipio...")
cantidad_dep = getCasosDepartamento(data_fallecidos)

print("Relacionando Coordenadas de Fallecidos y Lesionados...")
data_fallecidos['coordenada'] = data_fallecidos.apply(lambda row: relacionaCoordenadas(cantidad_dep
                                                                                       ,row.depto_ocu
                                                                                       ,row.mupio_ocu
                                                                                      )
                                                      , axis=1)


print("Transformando Hechos de Transito...")
data_hechos = getData('../Datos/02 - Hechos de Transito/')

print("Obteniendo coordenadas y cantidad de Hechos de Transito...")
cantidad_dep = getCasosDepartamento(data_hechos)

print("Relacionando Coordenadas de Hechos de Transito...")
data_hechos['coordenada'] = data_hechos.apply(lambda row: relacionaCoordenadas(cantidad_dep
                                                                                       ,row.depto_ocu
                                                                                       ,row.mupio_ocu
                                                                                      )
                                                      , axis=1)



print('Transformando Vehículos Involucrados...')
data_vehiculos = getData('../Datos/03 - Vehículos Involucrados/')

print("Obteniendo coordenadas y cantidad de Hechos de Transito...")
cantidad_dep = getCasosDepartamento(data_vehiculos)

print("Relacionando Coordenadas de Hechos de Transito...")
data_vehiculos['coordenada'] = data_vehiculos.apply(lambda row: relacionaCoordenadas(cantidad_dep
                                                                                       ,row.depto_ocu
                                                                                       ,row.mupio_ocu
                                                                                      )
                                                      , axis=1)

# list of dataframes and sheet names
frames = [data_fallecidos, data_hechos, data_vehiculos]
sheets = ['Fallecidos-Lesionados','Hechos-Transito','Vehiculos-Involucrados']

print("Exportando Datos...")
exportExcel(frames, sheets, output_path)

print("Proceso Terminado...")
