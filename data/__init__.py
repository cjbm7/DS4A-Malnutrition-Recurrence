import os
basedir = os.path.abspath(os.path.dirname(__file__))

dbase = os.path.join(basedir, 'db','predictions.db')

modelpk = os.path.join(basedir, 'model','CD_his_RF3.pickle')

dpto_mpio = os.path.join(basedir, 'dpto_mpio.parquet')
tomas_pq = os.path.join(basedir, 'tomas_max_500_act.parquet')