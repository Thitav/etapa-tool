import plotly.express as px
from math import nan, isnan
import streamlit as st
import pandas as pd
import httpx
import json

url_api = 'https://www.colegioetapa.com.br/ar-colegio-app-backend/v1'
url_login = url_api + '/login/aluno'
url_data = url_api + '/provas/notas?grau={}&local={}&matricula={}&serie={}&unidade={}'

client = httpx.Client(http2=True)


@st.cache
def load_data(user):
  data = client.get(url_data.format(user['grau'], user['local'], user['matricula'], user['serie'], user['unidade']),
                    headers={'Auth-Token': user['token'] + ':' + user['matricula']})
  data = json.loads(data.content.decode('utf-8'))['prvNotas']

  df = pd.DataFrame(data)
  df = df.drop(['class1', 'class2', 'class3', 'class4',
                'link1', 'link2', 'link3', 'link4'], axis=1)
  df = df.rename({'materia': 'Matéria', 'celula': 'Código',
                  'conj1': 'Conjunto 1', 'conj2': 'Conjunto 2',
                  'conj3': 'Conjunto 3', 'conj4': 'Conjunto 4'}, axis=1)
  df = df.replace({'---': nan, 'F*': nan, 'F**': nan})
  df[['Conjunto 1', 'Conjunto 2', 'Conjunto 3', 'Conjunto 4']] = df[[
      'Conjunto 1', 'Conjunto 2', 'Conjunto 3', 'Conjunto 4']].astype(float)
  df['Média'] = df[['Conjunto 1', 'Conjunto 2',
                    'Conjunto 3', 'Conjunto 4']].mean(axis=1)
  df[['Conjunto 1', 'Conjunto 2', 'Conjunto 3', 'Conjunto 4']].mean(axis=0)

  mean = []
  for i in df:
    for j in df[i]:
      if type(j) == float and not isnan(j):
        mean.append(j)
  mean = sum(mean) / len(mean)

  means = pd.DataFrame({'Média': df.drop('Média', axis=1).mean(axis=0)})

  return df, means, mean


def run():
  df, means, mean = load_data(st.session_state['user'])

  st.title('Notas')
  st.write(df)
  st.write('Média geral:')
  st.write(mean)

  st.title('Conjuntos')
  st.write(means.transpose())
  st.write(px.line(means, y='Média',  markers=True, range_y=[0, 10]))

  st.title('Matérias')
  st.write(px.bar(df[['Código', 'Média']].sort_values('Média'),
                  x='Código', y='Média', range_y=[0, 10]))
  code = st.selectbox('Código', df['Código'])
  submit = st.button('Gerar')

  if submit:
    data = df.loc[df['Código'] == code][['Conjunto 1', 'Conjunto 2',
                                         'Conjunto 3', 'Conjunto 4']]
    data = [float(data[i]) for i in data if not isnan(data[i])]
    data = pd.DataFrame({'Conjunto': [f'Conjunto {i+1}' for i in range(len(data))],
                        'Nota': data})
    st.write(px.line(data, x='Conjunto', y='Nota',
                     title=code, markers=True, range_y=[0, 10]))


with st.form('auth_form'):
  username = st.text_input('Matrícula')
  password = st.text_input('Senha', type='password')
  submit = st.form_submit_button('Carregar')

  if submit:
    data = client.post(url_login,
                       data={'matricula': username, 'senha': password})
    data = json.loads(data.content.decode('utf-8'))
    if 'body' in data.keys():
      st.session_state['user'] = data['body']
    else:
      st.error('Login inválido')

if 'user' in st.session_state:
  run()
