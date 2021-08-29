import os
import time
from app import app
from flask import json, render_template, request, url_for, redirect, send_from_directory, jsonify
from .logger import *
import json
import pandas as pd
import sqlite3
import duckdb
from .utils import predict_set, clf

basedir = os.path.abspath(os.path.dirname(__file__))
dbase = os.path.join(basedir, 'db','predictions.db')
tomas_pq = os.path.join(basedir, 'db','tomas_max_500.parquet')
ben_pq = os.path.join(basedir, 'db','datos_beneficiario.parquet')

from nanoid import generate   #Genera el id de la predicción
def uidg(largo=7):
	return generate('1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ', largo)


@app.route('/')  #Página de inicio
def inicio():
    context = {
        'pagina': 'DS4a Final Project - Recurrence of malnutrition in Colombia: Analysis and prediction of associated risk factors',
        }
    #return redirect(url_for('data_predict'))  #temporal
    return render_template('index.html', **context)


@app.route('/data_predict', methods=['GET', 'POST'])  #Página del predictor
def data_predict(id=None):
    id = request.args.get("id", None)
    context = {
    'pagina': 'Recurrence Predictor',
	  'idt': id,
    }
    return render_template('datapredict.html', **context)


@app.route('/regional')  #Pagina Dasboard Regional
def regional():
    context = {
        'pagina': 'Regional$',
        }
    return render_template('regional.html', **context)


@app.route('/splots')   #Pagina del Scatter plot dinámico( es un iFrame, el original está en /dash/scatter)
def splots():
    context = {
        'pagina': 'Scatterplots$',
        }
    return render_template('splot.html', **context)


@app.route('/sociomaps')   #Pagina de mapas sociodemos dinámico( es un iFrame, el original está en /dash/maps)
def sociomaps():
    context = {
        'pagina': 'Sociodemographic Maps$',
        }
    return render_template('sociomaps.html', **context)

@app.route('/boxplots')   #Pagina del box plot dinámico( es un iFrame, el original está en /dash/box plots)
def boxplots():
    context = {
        'pagina': 'Box Plots$',
        }
    return render_template('boxplots.html', **context)




@app.route('/predictor', methods=['POST']) #Es un endpoint que procesa la predición, retorna a la vista de prediccion con la ID
def predictor():
    if not request.method == 'POST':
        return {}
    f = request.files['data_file']
    ext = f.filename.split('.')[1].lower()
    if ext == 'csv':
        df = pd.read_csv(f)
    else: return {}
    #En esta linea ejecutar la funcion de predicción
    df = predict_set(df, clf)
    #df[predict] = ...
    df.fillna("", inplace=True)
    print(df.head())
    pre_dict=df.to_dict(orient="records")
    print(f'********************\n{pre_dict}\n**********************')
    data = {"data": pre_dict}
    idt = uidg(5)
    try:
        conn = sqlite3.connect(dbase)  #Guarda la predicción en un base de datos sqlite
        cursor = conn.cursor()
        idt = uidg(5)
        cursor.execute("insert into predicts values (?, ?)", [idt, json.dumps(data)])
        conn.commit()
        conn.close()
    except:
        print('//////////ERROR Al GUARDAR PREDICCIÓN///////////')
    return redirect(url_for('data_predict', id=idt))


@app.route('/pjson/<idt>')  # Es un endpoint que genera el Json de la predicción para mostrar en el datatable
def resp_json(idt):
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    pjson = cursor.execute(f"select pjson from predicts where id ='{idt}'").fetchone()
    conn.close()
    pjson = json.loads(pjson[0])
    return pjson

 
con = duckdb.connect()    #Inicialización de Duckdb para hacer query sobre un .parquet
con.execute("PRAGMA threads=2")
con.execute("PRAGMA enable_object_cache")

@app.route('/seguimiento/<idBeneficiario>')  #Vista de seguimiento nutricional
def seg_nutricional(idBeneficiario):
    names = ['IdToma', 'Registro', 'Vigencia', 'Toma', 'Servicio',
       'FechaValoracionNutricional', 'EdadMeses',
       'FechaMedicionPerimetroBraquial', 'MedicionPerimetroBraquial', 'Peso',
       'Talla', 'ZScoreTallaEdad', 'ZScorePesoEdad', 'ZScorePesoTalla',
       'ZScoreIMC', 'EstadoTallaEdad', 'EstadoPesoEdad', 'EstadoPesoTalla',
       'EstadoIMC', 'Flag', 'FechaRegistroSaludNutricion',
       'PresentaCarneVacunacion', 'ControlesCrecimDesarrollo',
       'AntecedentePremadurez', 'Direccion', 'IdBeneficiario', 'Id', 'FechaNacimiento', 'Sexo']
    try:
        inicio = time.time()
        query = f"SELECT * FROM '{tomas_pq}' WHERE IdBeneficiario = {idBeneficiario} ORDER by Toma DESC"
        ben = con.execute(query).fetchone()
        print(ben)
        zip_iter = zip(names, ben)
        context = dict(zip_iter)
        print(context)
        fin= time.time()
        print(f'//////////////// tiempo total: {fin-inicio}s\\\\\\\\\\\\\\')
    except:
        return 'Error al conectar tomas.parquet'

    context['FechaValoracionNutricional'] = context['FechaValoracionNutricional'].strftime('%Y-%m-%d')
    """
    try:
        query = f"SELECT FechaNacimiento, Sexo FROM '{ben_pq}' WHERE IdBeneficiario = {idBeneficiario} ORDER by Vigencia DESC"
        nacimiento, sexo = con.execute(query).fetchone()
    except:
        nacimiento, sexo = False
    """
    """genero = {'M': 'Masculino', 'F': 'Femenino', 'I': 'Intersexual'}
    if context['Sexo']: context['Sexo'] = genero[context['Sexo']]
    else: context['Sexo'] = 'Undisclosed' """
    
    if context['FechaNacimiento']: context['Nacimiento'] = context['FechaNacimiento'].strftime('%Y-%m-%d')
    else: context['Nacimiento'] = 'Undisclosed'
    return render_template('fichanutricional.html', **context)


@app.route('/pruebaj')  #Es un endpoin de prueba para generar json en los datatables de prueba, se eliminará luego
def prueba_json():
    data_json = [
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 45.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": "2019-11-05 15:51:25", 
      "FechaValoracionNutricional": "2019-10-29 00:00:00", 
      "Flag": 0.0, 
      "Id": 286646.0, 
      "IdBeneficiario": 8872, 
      "IdToma": 12, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 16.0, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 4699487, 
      "Servicio": "HCB TRADICIONAL- COMUNITARIO (T)", 
      "Talla": 103.0, 
      "Toma": 4, 
      "Vigencia": 2019, 
      "ZScoreIMC": -0.23, 
      "ZScorePesoEdad": -0.01, 
      "ZScorePesoTalla": -0.17, 
      "ZScoreTallaEdad": 0.2
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 0.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 64.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": '', 
      "EstadoPesoTalla": '', 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-07-12 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 10058, 
      "IdToma": 13, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 24.299999237060547, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988320, 
      "Servicio": "SERVICIO ESPECIAL PARA LA PRIMERA INFANCIA - GRADO TRANSICI\u00d3N CON ATENCI\u00d3N INTEGRAL", 
      "Talla": 121.4000015258789, 
      "Toma": 3, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.77, 
      "ZScorePesoEdad": '', 
      "ZScorePesoTalla": '', 
      "ZScoreTallaEdad": 2.1
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 0.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 67.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": '', 
      "EstadoPesoTalla": '', 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-10-20 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 10058, 
      "IdToma": 14, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 23.399999618530277, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988320, 
      "Servicio": "SERVICIO ESPECIAL PARA LA PRIMERA INFANCIA - GRADO TRANSICI\u00d3N CON ATENCI\u00d3N INTEGRAL", 
      "Talla": 123.3000030517578, 
      "Toma": 4, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.09, 
      "ZScorePesoEdad": '', 
      "ZScorePesoTalla": '', 
      "ZScoreTallaEdad": 2.14
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 52.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Riesgo de peso bajo para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Riesgo de baja talla", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-05-10 00:00:00", 
      "Flag": 0.0, 
      "Id": 3858760.0, 
      "IdBeneficiario": 15997, 
      "IdToma": 15, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 15.0, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988321, 
      "Servicio": "HCB TRADICIONAL- COMUNITARIO (T)", 
      "Talla": 100.5, 
      "Toma": 2, 
      "Vigencia": 2017, 
      "ZScoreIMC": -0.33, 
      "ZScorePesoEdad": -1.04, 
      "ZScorePesoTalla": -0.4, 
      "ZScoreTallaEdad": -1.27
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 55.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Riesgo de baja talla", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-08-03 00:00:00", 
      "Flag": 0.0, 
      "Id": 3858760.0, 
      "IdBeneficiario": 15997, 
      "IdToma": 16, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 17.0, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988321, 
      "Servicio": "HCB TRADICIONAL- COMUNITARIO (T)", 
      "Talla": 102.0, 
      "Toma": 3, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.81, 
      "ZScorePesoEdad": -0.27, 
      "ZScorePesoTalla": 0.77, 
      "ZScoreTallaEdad": -1.25
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 2.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 58.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Riesgo de baja talla", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-11-07 00:00:00", 
      "Flag": 0.0, 
      "Id": 3858760.0, 
      "IdBeneficiario": 15997, 
      "IdToma": 17, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 17.5, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988321, 
      "Servicio": "HCB TRADICIONAL- COMUNITARIO (T)", 
      "Talla": 103.0, 
      "Toma": 4, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.92, 
      "ZScorePesoEdad": -0.27, 
      "ZScorePesoTalla": 0.89, 
      "ZScoreTallaEdad": -1.38
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 49.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Riesgo de peso bajo para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-02-20 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 33714, 
      "IdToma": 18, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 14.5, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988322, 
      "Servicio": "CDI CON ARRIENDO - INSTITUCIONAL INTEGRAL", 
      "Talla": 101.0, 
      "Toma": 1, 
      "Vigencia": 2017, 
      "ZScoreIMC": -0.92, 
      "ZScorePesoEdad": -1.03, 
      "ZScorePesoTalla": -0.93, 
      "ZScoreTallaEdad": -0.69
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 51.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-05-08 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 33714, 
      "IdToma": 19, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 15.0, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988322, 
      "Servicio": "CDI CON ARRIENDO - INSTITUCIONAL INTEGRAL", 
      "Talla": 102.0, 
      "Toma": 2, 
      "Vigencia": 2017, 
      "ZScoreIMC": -0.7, 
      "ZScorePesoEdad": -0.95, 
      "ZScorePesoTalla": -0.73, 
      "ZScoreTallaEdad": -0.77
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 54.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-07-27 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 33714, 
      "IdToma": 20, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 15.5, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988322, 
      "Servicio": "CDI CON ARRIENDO - INSTITUCIONAL INTEGRAL", 
      "Talla": 103.0, 
      "Toma": 3, 
      "Vigencia": 2017, 
      "ZScoreIMC": -0.51, 
      "ZScorePesoEdad": -0.88, 
      "ZScorePesoTalla": -0.55, 
      "ZScoreTallaEdad": -0.86
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 1.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 57.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Talla adecuada para la edad", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-10-26 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 33714, 
      "IdToma": 21, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 16.5, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988322, 
      "Servicio": "CDI CON ARRIENDO - INSTITUCIONAL INTEGRAL", 
      "Talla": 104.0, 
      "Toma": 4, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.03, 
      "ZScorePesoEdad": -0.61, 
      "ZScorePesoTalla": -0.02, 
      "ZScoreTallaEdad": -0.98
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": '', 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 50.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Riesgo de peso bajo para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Retraso en talla", 
      "FechaMedicionPerimetroBraquial": "2017-03-22 00:00:00", 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-03-21 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 33748, 
      "IdToma": 22, 
      "MedicionPerimetroBraquial": 20.0, 
      "Peso": 14.600000381469728, 
      "PresentaCarneVacunacion": "N", 
      "Registro": 988323, 
      "Servicio": "SERVICIO ESPECIAL PARA LA PRIMERA INFANCIA - INSTITUCIONAL INTEGRAL", 
      "Talla": 95.5, 
      "Toma": 1, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.54, 
      "ZScorePesoEdad": -1.06, 
      "ZScorePesoTalla": 0.36, 
      "ZScoreTallaEdad": -2.13
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": '', 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 57.0, 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": "Riesgo de peso bajo para la edad", 
      "EstadoPesoTalla": "Peso adecuado para la talla", 
      "EstadoTallaEdad": "Retraso en talla", 
      "FechaMedicionPerimetroBraquial": "2017-10-25 00:00:00", 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-10-18 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 33748, 
      "IdToma": 23, 
      "MedicionPerimetroBraquial": 20.0, 
      "Peso": 14.600000381469728, 
      "PresentaCarneVacunacion": "N", 
      "Registro": 988323, 
      "Servicio": "SERVICIO ESPECIAL PARA LA PRIMERA INFANCIA - INSTITUCIONAL INTEGRAL", 
      "Talla": 95.5, 
      "Toma": 4, 
      "Vigencia": 2017, 
      "ZScoreIMC": 0.58, 
      "ZScorePesoEdad": -1.54, 
      "ZScorePesoTalla": 0.36, 
      "ZScoreTallaEdad": -2.86
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 0.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": 48.0, 
      "EstadoIMC": "Sobrepeso", 
      "EstadoPesoEdad": "Peso adecuado para la edad", 
      "EstadoPesoTalla": "Sobrepeso", 
      "EstadoTallaEdad": "Retraso en talla", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-02-01 00:00:00", 
      "Flag": 0.0, 
      "Id": '', 
      "IdBeneficiario": 39848, 
      "IdToma": 24, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 15.300000190734863, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988324, 
      "Servicio": "HCB TRADICIONAL- COMUNITARIO (T)", 
      "Talla": 88.0, 
      "Toma": 1, 
      "Vigencia": 2017, 
      "ZScoreIMC": 2.94, 
      "ZScorePesoEdad": -0.57, 
      "ZScorePesoTalla": 2.5, 
      "ZScoreTallaEdad": -3.71
    }, 
    {
      "AntecedentePremadurez": '', 
      "ControlesCrecimDesarrollo": 2.0, 
      "Direccion": "Primera Infancia", 
      "EdadMeses": '', 
      "EstadoIMC": "Adecuado para la edad", 
      "EstadoPesoEdad": '', 
      "EstadoPesoTalla": '', 
      "EstadoTallaEdad": "Retraso en talla", 
      "FechaMedicionPerimetroBraquial": '', 
      "FechaRegistroSaludNutricion": '', 
      "FechaValoracionNutricional": "2017-05-04 00:00:00", 
      "Flag": 1.0, 
      "Id": '', 
      "IdBeneficiario": 50556, 
      "IdToma": 25, 
      "MedicionPerimetroBraquial": '', 
      "Peso": 9.350000381469728, 
      "PresentaCarneVacunacion": "S", 
      "Registro": 988325, 
      "Servicio": "SERVICIO ESPECIAL PARA LA PRIMERA INFANCIA - INSTITUCIONAL INTEGRAL", 
      "Talla": 73.0, 
      "Toma": 2, 
      "Vigencia": 2017, 
      "ZScoreIMC": -0.2, 
      "ZScorePesoEdad": '', 
      "ZScorePesoTalla": '', 
      "ZScoreTallaEdad": ''
    }]
    data = {
        "data": data_json}

    return jsonify(data)
