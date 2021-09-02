import os
import time
import datetime
from app import app
from flask import json, render_template, request, url_for, redirect, send_from_directory, jsonify
from .logger import *
import json
import pandas as pd
import sqlite3
import duckdb
from .utils import predict_set, clf, pred_risk, latest_pred
from .misc import contacts, dptos, cols
from data import *


from nanoid import generate   #Genera el id de la predicción
def uidg(largo=7):
	return generate('1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ', largo)


@app.route('/')  #Página de inicio
def inicio():
    context = {
        'pagina': 'DS4a Final Project - Recurrence of malnutrition in Colombia: Analysis and prediction of associated risk factors',
        'all_contacts': contacts
        }
    return render_template('index.html', **context)#, all_contacts=contacts)


@app.route('/data_predict', methods=['GET', 'POST'])  #Página del predictor
def data_predict(id=None):
    id = request.args.get("id", None)
    latest = latest_pred()
    print(latest)
    context = {
    'pagina': 'Recurrence Predictor',
	'idt': id,
    'latest': latest
    }
    return render_template('datapredict.html', **context)


@app.route('/regional')  #Pagina Dasboard Regional
def regional():
    context = {
        'pagina': 'Regional$',
        'dptos': dptos
        }
    return render_template('regional.html', **context)



@app.route('/municipios/<dpto>')
def mpios(dpto):
  con = duckdb.connect()    #Inicialización de Duckdb para hacer query sobre un .parquet
  con.execute("PRAGMA threads=2")
  con.execute("PRAGMA enable_object_cache")
  query = f"SELECT cod_mpio, nom_mpio FROM '{dpto_mpio}' WHERE cod_dpto = {dpto} ORDER by nom_mpio"
  mpios = con.execute(query).fetchall()
  if mpios:
    lista = []
    for row in mpios:
      mpio = {}
      mpio['cod'] = row[0]
      mpio['nom'] = row[1]
      lista.append(mpio)
    data = {"data": lista}
    return jsonify(data)
  else:
    return {}


@app.route('/splots')   #Pagina del Scatter plot dinámico( es un iFrame, el original está en /dash/scatter)
def splots():
    context = {
        'pagina': 'Scatterplots$',
        }
    return render_template('splot.html', **context)


@app.route('/sociomaps')   #Pagina de mapas sociodemos dinámico( es un iFrame, el original está en /dash/maps)
def sociomaps():
    context = {
        'pagina': 'Sociodemographics',
        }
    return render_template('sociomaps.html', **context)


@app.route('/boxplots')   #Pagina del box plot dinámico( es un iFrame, el original está en /dash/box plots)
def boxplots():
    context = {
        'pagina': 'Box-Plots',
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
    df = predict_set(df, clf)
    print(df.columns)
    df.fillna("", inplace=True)
    #print(df.head())
    cant = len(df)
    pre_dict=df.to_dict(orient="records")
    data = {"data": pre_dict}
    idt = uidg(5)
    try:
        conn = sqlite3.connect(dbase)  #Guarda la predicción en un base de datos sqlite
        cursor = conn.cursor()
        idt = uidg(5)
        cursor.execute("insert into predicts (id, pjson, cant) values (?, ?, ?)", [idt, json.dumps(data), cant])
        conn.commit()
        conn.close()
    except:
        print('//////////ERROR Al GUARDAR PREDICCIÓN///////////')
    return redirect(url_for('data_predict', id=idt))


@app.route('/pjson/<idt>')  # Es un endpoint que genera el Json de la predicción para mostrar en el datatable
def resp_json(idt):
    if idt == '':
      return {}
    conn = sqlite3.connect(dbase)
    cursor = conn.cursor()
    pjson = cursor.execute(f"select pjson from predicts where id ='{idt}'").fetchone()
    conn.close()
    pjson = json.loads(pjson[0])
    return pjson


@app.route('/seguimiento/<idBeneficiario>')  #Vista de seguimiento nutricional
def seg_nutricional(idBeneficiario):
    col_query = ', '.join(cols)
    try:
        inicio = time.time()
        con = duckdb.connect()    #Inicialización de Duckdb para hacer query sobre un .parquet
        con.execute("PRAGMA threads=2")
        con.execute("PRAGMA enable_object_cache")
        query = f"SELECT {col_query} FROM '{tomas_pq}' WHERE IdBeneficiario = {idBeneficiario} ORDER by Toma DESC"
        ben = con.execute(query).fetchone()
        print(ben)
        zip_iter = zip(cols, ben)
        context = dict(zip_iter)
        #print(context)
        fin= time.time()
        print(f'//////////////// tiempo total: {fin-inicio}s\\\\\\\\\\\\\\')
    except:
        return 'Error al conectar tomas.parquet'
    context['Prediction'] = 0.30     # Corregir
    context['FechaValoracionNutricional'] = context['FechaValoracionNutricional'].strftime('%Y-%m-%d')
    if context['FechaNacimiento']: context['FechaNacimiento'] = context['FechaNacimiento'].strftime('%Y-%m-%d')
    else: context['FechaNacimiento'] = 'Undisclosed'
    try:
      risk = pred_risk(context['Prediction'])
      context['Prediction'] = str (context['Prediction'] * 100) + '% - ' + risk
    except:
      context['Prediction'] = 'N.D.'
    datetim = datetime.datetime.now()
    context['Datetime'] = datetim.strftime('%Y-%m-%d, %H:%M')
    #return jsonify(context)
    return render_template('fichanutricional.html', **context)


@app.route('/data_json/<dpto>/<mpio>', methods=['GET','POST'])
def data_json(dpto='all', mpio='all'):
    col_query = ', '.join(cols)
    if mpio != 'all':
      query = f"SELECT {col_query} FROM '{tomas_pq}' WHERE cod_mpio = '{mpio}' LIMIT 500"
    elif dpto != 'all':
      query = f"SELECT {col_query} FROM '{tomas_pq}' WHERE cod_dpto = '{dpto}' LIMIT 500"
    else:
      query = f"SELECT {col_query} FROM '{tomas_pq}' LIMIT 500"
    
    try:
        inicio = time.time()
        con = duckdb.connect()    #Inicialización de Duckdb para hacer query sobre un .parquet
        con.execute("PRAGMA threads=2")
        con.execute("PRAGMA enable_object_cache")
        #qry = con.execute(query).fetchall()
        qry = con.execute(query).df()
        qry = qry.sample(150)
        qry.fillna("", inplace=True)
        #print(qry)
        toms = qry.to_dict(orient="records")
        """toms = []
        for item in qry:
          zip_iter = zip(cols, item)
          ben_dict = dict(zip_iter)
          toms.append(ben_dict)"""
        fin= time.time()
        print(f'//////////////// tiempo total: {fin-inicio}s\\\\\\\\\\\\\\')
        data = {
            "data": toms}
        return jsonify(data)
    except:
        return 'Error al conectar tomas.parquet'
