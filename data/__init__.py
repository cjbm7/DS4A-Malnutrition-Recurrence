import os

basedir = os.path.abspath(os.path.dirname(__file__))

dbase = os.path.join(basedir, 'db','predictions.db')

modelpk = os.path.join(basedir, 'model','CD_his_RF3.pickle')

dpto_mpio = os.path.join(basedir, 'core','dpto_mpio.parquet')
tomas_pq = os.path.join(basedir, 'core','tomas_max_500_act.parquet')

tom3000_pq = os.path.join(basedir, 'plots','tomas_3000_act.parquet')
boxplots_pq = os.path.join(basedir, 'plots','data_frame_to_boxplot.parquet')
socio_eda_mpios = os.path.join(basedir, 'plots','sociodemo_EDA_mcpio.parquet')
geojson_mpios = os.path.join(basedir, 'plots', 'co_2018_MGN_MPIO_POLITICO.geojson')
points_z = os.path.join(basedir, 'plots', 'puntos_peso_talla.csv')