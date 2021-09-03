import pandas as pd
import numpy as np
import joblib
import os
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from nanoid import generate 
from data import modelpk
from data import dbase

clf = joblib.load(modelpk)

import numpy as np

# New function
cols_model = {
    'clf3': ['EdadMeses',
           'ZScorePesoTalla',
           'ZScoreIMC'],
    'rf3': ['EdadMeses',
          'Peso',
          'Talla',
          'ZScoreTallaEdad',
          'ZScorePesoEdad',
          'ZScorePesoTalla',
          'ZScoreIMC']
    }
english = {
      'IdToma':'IdTake',
      'Registro': 'Record',
      'Vigencia': 'Year',
      'Toma': 'Take',
      'Servicio': 'Service',
      'FechaValoracionNutricional': 'Date nutr assessment',
      'EdadMeses': 'Age (mo)',
      'FechaMedicionPerimetroBraquial': 'Date arm circ measurement',
      'MedicionPerimetroBraquial': 'Arm circunference',
      'Peso': 'Weight',
      'Talla': 'Height', 
      'ZScoreTallaEdad': 'Height-for-age z-score',
      'ZScorePesoEdad': 'Weight-for-age z-score',
      'ZScorePesoTalla': 'Weight-for-height z-score',
      'ZScoreIMC': 'IMC z-score',
      'EstadoTallaEdad': 'Height-for-age status',
      'EstadoPesoEdad': 'Weight-for-age status',
      'EstadoPesoTalla': 'Weight-for-height status',
      'EstadoIMC': 'IMC status',
      'Flag': 'Flags',
      'FechaRegistroSaludNutricion': 'Date registration',
      'PresentaCarneVacunacion': 'Vaccination card',
      'ControlesCrecimDesarrollo': 'Growth and development control',
      'AntecedentePremadurez': 'Prematurity antecedent',
      'Direccion': 'Direction',
      'IdBeneficiario': 'IdBeneficiary',
      #'Id',
      'Riesgo desnutricion (1 meses)': 'Undernutrition risk (1 mo)',
      'Riesgo desnutricion (2 meses)': 'Undernutrition risk (2 mo)',
      'Riesgo desnutricion (3 meses)': 'Undernutrition risk (3 mo)',
      }
  
def predict_set(dataset, model, cols_input=cols_model['clf3'], time=3, depth=2):
  df = dataset.sort_values(['IdBeneficiario', 'EdadMeses'])
  df = df.dropna(subset=cols_input).reset_index(drop=True)
  his_list = list()
  for i in range(depth - 1, len(df)):
    id = df.loc[i, 'IdBeneficiario']
    if (df.loc[i - depth + 1, 'IdBeneficiario'] == id):
      fragmento = df.loc[i - depth + 1: i].reset_index(drop=True).\
        reset_index(drop=False)
      melted = fragmento.melt(id_vars='index', value_vars=cols_input)
      melted['varname'] = melted.\
        apply(lambda x: x['variable'] + '-' + str(depth - x['index']), axis='columns')
      melted['IdBeneficiario'] = [id] * len(melted)
      pivot = melted.pivot(index='IdBeneficiario', columns='varname', values='value').\
        reset_index(drop=False)
      pivot['EdadMeses-0'] = pivot['EdadMeses-1'] + 3
      his_list.append(pivot)
  his = pd.concat(his_list, axis='index').dropna()
  Ids = his['IdBeneficiario']
  X = his.drop(columns=['IdBeneficiario'])
  y = [round(q, 2) for p, q in model.predict_proba(X)]
  
  prediction = pd.DataFrame({'IdBeneficiario': Ids,
                             f'Riesgo desnutricion ({time} meses)': y})
  prediction = prediction.drop_duplicates(subset=['IdBeneficiario'], keep='last')
  data = df.drop_duplicates(subset=['IdBeneficiario'], keep='last')
  result =  data.merge(prediction, on='IdBeneficiario', how='left')
  return result

def translate_dataframe(df, dictionary):
  return df.rename(columns=dictionary)


# Old function
def predict_set_one_model(dataset, model):
  df = dataset.sort_values(['IdBeneficiario', 'EdadMeses'])
  cols_modelo = [
                 'EdadMeses',
                 'ZScorePesoTalla',
                 'ZScoreIMC', 'Peso', 'Talla'] #Se agrega Peso y Talla
  df = df.dropna(subset=cols_modelo).reset_index(drop=True)
  prof = 2 # Profundidad del modelo
  his_list = list()
  for i in range(prof - 1, len(df)):
    id = df.loc[i, 'IdBeneficiario']
    if (df.loc[i - prof + 1, 'IdBeneficiario'] == id):
      fragmento = df.loc[i - prof + 1: i].reset_index(drop=True).\
        reset_index(drop=False)
      melted = fragmento.melt(id_vars='index', value_vars=cols_modelo)
      melted['varname'] = melted.\
        apply(lambda x: x['variable'] + '-' + str(prof - x['index']), axis='columns')
      melted['IdBeneficiario'] = [id] * len(melted)
      pivot = melted.pivot(index='IdBeneficiario', columns='varname', values='value').\
        reset_index(drop=False)
      pivot['EdadMeses-0'] = pivot['EdadMeses-1'] + 3
      his_list.append(pivot)
  his = pd.concat(his_list, axis='index').dropna()
  #Ids = his['IdBeneficiario']
  #X = his.drop(columns=['IdBeneficiario'])
  colx = ['EdadMeses-1', 'EdadMeses-2', 'ZScoreIMC-1', 'ZScoreIMC-2', 'ZScorePesoTalla-1',
          'ZScorePesoTalla-2', 'EdadMeses-0']  #Agregado
  y = [q for p, q in model.predict_proba(his[colx])]  #Toma solo las columnas que requiere el modelo
  probs = pd.Series(y) # Lineas agregadas para ajustar la salida esperada del Datatable
  his = his.reset_index()
  his['RiesgoDesnutricion3Meses'] = probs
  his = his.drop_duplicates(subset=['IdBeneficiario'], keep='last')
  return his[['IdBeneficiario', 'EdadMeses-0', 'Peso-1', 'Talla-1', 'ZScoreIMC-1',
              'ZScorePesoTalla-1', 'RiesgoDesnutricion3Meses']]


def nutrition_monitoring_plot(IdBeneficiario, dataset, points, lang='english'):
  '''Retorna la gráfica de seguimiento nutricional para un beneficiario, a partir de su 
  identificador IdBeneficiario en un dataset de tomas nutricionales, incluyendo:
  'Sexo', 'Talla', 'Peso', 'EstadoPesoTalla', 'EstadoPesoTalla', 'ZScorePesoTalla', 'EdadMeses',
  'FechaValoracionNutricional'
  import pandas as pd
  import numpy as np
  import plotly.express as px
  import plotly.graph_objects as go
  '''
  # Constantes
  # Las siguientes definiciones pueden colocarse antes de ejecutar la función
  z_scores = [i - 3 for i in range(7)]
  color_palette = ['green', 'goldenrod', 'red', 'black']
  color_estado = {
      'Desnutrición aguda severa': 'black',
      'Desnutrición aguda moderada': 'red',
      'Riesgo de desnutrición aguda': 'goldenrod',
      'Peso adecuado para la talla': 'green',
      'Riesgo de sobrepeso': 'goldenrod',
      'Sobrepeso': 'red',
      'Obesidad': 'black',
      }
  cols_plot = ['Sexo', 'FechaValoracionNutricional', 'EdadMeses', 'Talla', 'Peso', 
              'ZScorePesoTalla', 'EstadoPesoTalla']
  english = {
    'Desnutrición aguda severa': 'Severely wasted',
    'Desnutrición aguda moderada': 'Wasted',
    'Riesgo de desnutrición aguda': 'Risk of wasting',
    'Peso adecuado para la talla': 'Normal weight for height',
    'Riesgo de sobrepeso': 'Risk of overweight',
    'Sobrepeso': 'Overweight',
    'Obesidad': 'Obesity',
    'plot title': 'Nutritional monitoring',
    'x axis': 'Height (cm)',
    'y axis': 'Weight (kg)',
    'legend title': 'Nutritional status (Weight-for-height)'
    }
    
  spanish = {
    'Desnutrición aguda severa': 'Desnutrición aguda severa',
    'Desnutrición aguda moderada': 'Desnutrición aguda moderada',
    'Riesgo de desnutrición aguda': 'Riesgo de desnutrición aguda',
    'Peso adecuado para la talla': 'Peso adecuado para la talla',
    'Riesgo de sobrepeso': 'Riesgo de sobrepeso',
    'Sobrepeso': 'Sobrepeso',
    'Obesidad': 'Obesidad',
    'plot title': 'Seguimiento nutricional',
    'x axis': 'Talla (cm)',
    'y axis': 'Peso (kg)',
    'legend title': 'Estado nutricional (Peso/Talla)'
    }
  # Variables
  df = dataset.loc[dataset['IdBeneficiario'] == IdBeneficiario, cols_plot].dropna()
  sex = df['Sexo'].iloc[0]
  
  if lang == 'spanish':
    language = spanish
  else:
    language = english
  
  fig = px.scatter(df, x='Talla', y='Peso', color='EstadoPesoTalla',
                  hover_data=['EstadoPesoTalla', 'ZScorePesoTalla', 'EdadMeses'],
                  hover_name='FechaValoracionNutricional',
                  color_discrete_map=color_estado)
                  #labels = {'EstadoPesoTalla': language['legend title']})
  fig.layout = dict(paper_bgcolor='white',
                    plot_bgcolor='white',
                    xaxis = dict(title = language['x axis'],
                                 showgrid=True,
                                 gridwidth=1,
                                 gridcolor='gray',
                                 range=[45, 120],
                                 mirror=True,
                                 ticks='outside',
                                 showline=True,
                                 linewidth=2,
                                 linecolor='black',
                                 tickvals=[10 * i for i in range(4, 13)]),
                    yaxis = dict(title = language['y axis'],
                                 showgrid=True,
                                 gridwidth=1,
                                 gridcolor='gray',
                                 range=[0, 34],
                                 mirror=True,
                                 ticks='outside',
                                 showline=True,
                                 linewidth=2,
                                 linecolor='black',
                                 tickvals=[2 * i for i in range(18)]),
                    font=dict(size=14),
                    legend=dict(bgcolor='white',
                                borderwidth=1))
  fig.for_each_trace(lambda t: t.update(name = language[t.name]))
  fig.add_trace(go.Scatter(x=df['Talla'], y=df['Peso'],
                          mode='lines', showlegend=False,
                          line=dict(color='black', width=1)))
  fig.update_layout(title= f"{language['plot title']}: {IdBeneficiario}")
  for z in z_scores:
    fig.add_trace(go.Scatter(x=points['height'], y=points[f'weight_{sex}_{z}'],
                            hoverinfo = 'none', showlegend=False,
                            line=dict(color=color_palette[abs(z)], width=1)))
  return fig


def pred_risk(prediction):
  if prediction > 0.75 : return 'Very high'
  elif prediction > 0.49 : return 'High'
  elif prediction > 0.30 : return 'Moderate'
  else: return 'Low'


def latest_pred():
  conn = sqlite3.connect(dbase)
  cursor = conn.cursor()
  query = f"SELECT id, cant, Timestamp FROM predicts ORDER by Timestamp DESC Limit 4"
  predicts = cursor.execute(query).fetchall()
  conn.close()
  return predicts

#Genera el id de la predicción
def uidg(largo=7):
	return generate('1234567890aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ', largo)
