import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

st.set_page_config(page_title="Simulação Semanal + ML", layout="wide")
st.title("Simulação Semanal Completa + Previsão com Machine Learning")

uploaded_file = st.file_uploader("Faça upload do CSV com a semana completa", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # ===== TRATAMENTO DE DATA E HORA =====
    df["Data"] = pd.to_datetime(df["Data"])
    df["Datetime"] = df["Data"] + pd.to_timedelta(df["Hora"] + ":00")
    df = df.sort_values("Datetime")
    
    # ===== CÁLCULOS =====
    df["Capacidade_ton_hora"] = df["Equipe_Disponivel"] * (3600 / 34)
    df["Acumulacao"] = (df["Chegada_Ton"].cumsum() - df["Saida_Priorizada"].cumsum()).clip(lower=0)

    # ===== ANÁLISE DA SEMANA =====
    st.success(f"Semana carregada: {df['Data'].dt.strftime('%d/%m').min()} até {df['Data'].dt.strftime('%d/%m').max()}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Carga total chegada", f"{df['Chegada_Ton'].sum():.0f} ton")
    with col2: st.metric("Carga total saída", f"{df['Saida_Priorizada'].sum():.0f} ton")
    with col3: st.metric("Pico de acumulação", f"{df['Acumulacao'].max():.0f} ton")
    with col4: st.metric("Média diária de pico", f"{df.groupby(df['Data'].dt.date)['Acumulacao'].max().mean():.1f} ton")

    # ===== GRÁFICO DA SEMANA INTEIRA =====
    fig_semana = px.line(df, x="Datetime", y="Acumulacao", 
                         title="Acumulação de Carga - Semana Completa",
                         markers=False, height=600)
    fig_semana.add_vline(x=df["Datetime"].iloc[0] + pd.Timedelta(days=1), line_dash="dot")
    fig_semana.add_vline(x=df["Datetime"].iloc[0] + pd.Timedelta(days=2), line_dash="dot")
    fig_semana.add_vline(x=df["Datetime"].iloc[0] + pd.Timedelta(days=3), line_dash="dot")
    fig_semana.add_vline(x=df["Datetime"].iloc[0] + pd.Timedelta(days=4), line_dash="dot")
    fig_semana.add_vline(x=df["Datetime"].iloc[0] + pd.Timedelta(days=5), line_dash="dot")
    fig_semana.add_vline(x=df["Datetime"].iloc[0] + pd.Timedelta(days=6), line_dash="dot")
    st.plotly_chart(fig_semana, use_container_width=True)

    # ===== MACHINE LEARNING (Random Forest - muito melhor que Regressão Linear) =====
    df["Dia_da_semana"] = df["Data"].dt.weekday   # 0=segunda, 6=domingo
    df["Minutos_do_dia"] = df["Datetime"].dt.hour * 60 + df["Datetime"].dt.minute

    X = df[["Dia_da_semana", "Minutos_do_dia", "Chegada_Ton", "Equipe_Disponivel"]]
    y = df["Acumulacao"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    st.success("Modelo Random Forest treinado com todos os dias da semana!")

    # ===== PREVISÃO PARA PRÓXIMO DIA =====
    st.subheader("Previsão para um novo dia")
    col1, col2 = st.columns(2)
    with col1:
        dia_semana = st.selectbox("Dia da semana", 
                                  options=[0,1,2,3,4,5,6], 
                                  format_func=lambda x: ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"][x])
    with col2:
        equipe_dia = st.number_input("Equipe disponível nesse dia", min_value=1, value=2)

    previsao_lista = []
    for hora in range(4, 24):
        minutos = hora * 60
        # assumindo chegada média histórica por hora (você pode mudar)
        chegada_media = df[df["Datetime"].dt.hour == hora]["Chegada_Ton"].mean()
        pred = model.predict([[dia_semana, minutos, chegada_media, equipe_dia]])[0]
        previsao_lista.append({"Hora": f"{hora:02d}:00", "Previsao_Acumulacao": max(0, pred)})

    df_prev = pd.DataFrame(previsao_lista)
    fig_prev = px.line(df_prev, x="Hora", y="Previsao_Acumulacao", title=f"Previsão de acumulação - {'Segunda Terça Quarta Quinta Sexta Sábado Domingo'.split()[dia_semana]}")
    st.plotly_chart(fig_prev, use_container_width=True)

else:
    st.info("Faça upload do arquivo CSV com a semana completa para começar a análise")
    st.download_button("Baixar exemplo de 7 dias", 
                       data=open("dados_semana_completa.csv", "rb").read(), 
                       file_name="dados_semana_completa.csv", 
                       mime="text/csv")

# Adicione o arquivo dados_semana_completa.csv na raiz do seu projeto no Streamlit Cloud
