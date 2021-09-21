from datetime import date
import os

import pandas as pd
import numpy as np

data_inicio = date.today()
print(data_inicio)


#Obtem o DF do CDI Diário
def consulta_bc(codigo_bcb):
    url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(codigo_bcb)
    df = pd.read_json(url)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df.set_index('data', inplace=True)
    # filtro = (df.index >= data_inicio)
    # df_filtrado = df[filtro]
    return df

cdi = consulta_bc(12)
cdi.columns = ['CDI'] 
print(cdi.tail(10)) #10 = número de dias para buscar os dados

print('- - '*12)

dolar = consulta_bc(1)
dolar.columns = ['PTAX']
print(dolar.tail(10)['PTAX']) #10 = número de dias para buscar os dados
