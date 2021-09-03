import os

basedir = os.path.abspath(os.path.dirname(__file__))

dbase = os.path.join(basedir, 'db','predictions.db')

modelpk = os.path.join(basedir, 'model','CD_his_RF3.pickle') 

dpto_mpio = os.path.join(basedir, 'core','dpto_mpio.parquet')

tomas_pq = os.path.join(basedir, 'core','tomas_max_50_act.parquet') #Vista regional y seguimiento nutricional
#tomas_pq = os.path.join(basedir, 'core','tomas_max_500_act.parquet') #Vista regional y seguimiento nutricional

incid_mpio = os.path.join(basedir, 'incidence','incidencia_mpio_act.parquet')
incid_dpto = os.path.join(basedir, 'incidence','incidencia_dpto_act.parquet')

tom3000_pq = os.path.join(basedir, 'plots','tomas_3000.parquet')  #Scatterplot
#tom3000_pq = os.path.join(basedir, 'plots','tomas_3000_act.parquet')  #Scatterplot
boxplots_pq = os.path.join(basedir, 'plots','data_frame_to_boxplot.parquet')  

socio_eda_mpios = os.path.join(basedir, 'plots','sociodemo_mpio_act.parquet') #heatmaps sociodemo
socio_eda_dptos = os.path.join(basedir, 'plots','sociodemo_dpto_act.parquet')

geojson_mpios = os.path.join(basedir, 'plots', 'co_2018_MGN_MPIO_POLITICO.geojson') #mapas
points_z = os.path.join(basedir, 'plots', 'puntos_peso_talla.csv') #Lineas gias 