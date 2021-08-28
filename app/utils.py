import pandas as pd
import numpy as np
import joblib
import os

basedir = os.path.abspath(os.path.dirname(__file__))
modelpk = os.path.join(basedir, 'db','CD_his_RF3.pickle')

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