import pandas as pd
import numpy as np
import joblib
import os
import plotly.express as px
import plotly.graph_objects as go
from data import modelpk

clf = joblib.load(modelpk)

import numpy as np
def predict_set(dataset, model):
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


def nutrition_monitoring_plot(IdBeneficiario, dataset, points, lang):
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
    'EstadoPesoTalla=Desnutrición aguda severa': 'Severely wasted',
    'EstadoPesoTalla=Desnutrición aguda moderada': 'Wasted',
    'EstadoPesoTalla=Riesgo de desnutrición aguda': 'Risk of wasting',
    'EstadoPesoTalla=Peso adecuado para la talla': 'Normal weight for height',
    'EstadoPesoTalla=Riesgo de sobrepeso': 'Risk of overweight',
    'EstadoPesoTalla=Sobrepeso': 'Overweight',
    'EstadoPesoTalla=Obesidad': 'Obesity',
    'plot title': 'Nutritional monitoring',
    'x axis': 'Height (cm)',
    'y axis': 'Weight (kg)',
    'legend title': 'Nutritional status (Weight-for-height)'
    }
  spanish = {
    'EstadoPesoTalla=Desnutrición aguda severa': 'Desnutrición aguda severa',
    'EstadoPesoTalla=Desnutrición aguda moderada': 'Desnutrición aguda moderada',
    'EstadoPesoTalla=Riesgo de desnutrición aguda': 'Riesgo de desnutrición aguda',
    'EstadoPesoTalla=Peso adecuado para la talla': 'Peso adecuado para la talla',
    'EstadoPesoTalla=Riesgo de sobrepeso': 'Riesgo de sobrepeso',
    'EstadoPesoTalla=Sobrepeso': 'Sobrepeso',
    'EstadoPesoTalla=Obesidad': 'Obesidad',
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
