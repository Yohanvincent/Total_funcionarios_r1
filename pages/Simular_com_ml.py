import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import plotly.express as px

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(page_title="Simular com ML", layout="wide")
st.title("Simular Capacidade e Previsão com Machine Learning")   # emoji removido

# ==================== UPLOAD DO ARQUIVO ====================
uploaded_file = st.file_uploader(
    "Faça upload do seu CSV com os dados de carga e equipe",
    type=["csv"],
    help="Colunas obrigatórias: Hora, Chegada_Ton, Saida_Priorizada, Equipe_Disponivel"
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("Arquivo carregado com sucesso!")
        st.dataframe(df.head(10))

        # ==================== PRÉ-PROCESSAMENTO ====================
        df["Hora_dt"] = pd.to_datetime(df["Hora"], format="%H:%M", errors="coerce")
        df["Minutos_do_dia"] = df["Hora_dt"].dt.hour * 60 + df["Hora_dt"].dt.minute

        # Garante colunas numéricas
        for col in ["Chegada_Ton", "Saida_Priorizada", "Equipe_Disponivel"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Capacidade por hora (34s médio por operação)
        df["Capacidade_ton_hora"] = df["Equipe_Disponivel"] * (3600 / 34)

        # Acumulação de carga
        df["Acumulacao"] = (df["Chegada_Ton"].cumsum() - df["Saida_Priorizada"].cumsum()).clip(lower=0)

        # ==================== MACHINE LEARNING ====================
        X = df[["Minutos_do_dia", "Chegada_Ton", "Equipe_Disponivel"]]
        y = df["Acumulacao"]

        if len(df) >= 5:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            st.write(f"**Erro Médio Absoluto (MAE):** {mae:.2f} toneladas")
        else:
            st.warning("Poucos dados para treinar. Usando apenas simulação.")
            model = None

        # ==================== PREVISÃO INTERATIVA ====================
        st.subheader("Faça sua própria previsão")
        col1, col2, col3 = st.columns(3)
        with col1:
            hora_input = st.time_input("Horário", value=pd.to_datetime("14:00").time())
        with col2:
            chegada = st.number_input("Chegada (ton)", min_value=0.0, value=5.0)
        with col3:
            equipe = st.number_input("Equipe disponível", min_value=0, value=2, step=1)

        minutos = hora_input.hour * 60 + hora_input.minute

        if model is not None:
            previsao = model.predict([[minutos, chegada, equipe]])[0]
            st.success(f"Previsão às {hora_input.strftime('%H:%M')}: **{previsao:.2f} ton**")
        else:
            st.info("Modelo ainda não treinado (poucos dados).")

        # ==================== GRÁFICOS ====================
        st.subheader("Gráficos")
        fig1 = px.line(df, x="Hora", y="Acumulacao", title="Acumulação de Carga", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(df, x="Hora", y=["Chegada_Ton", "Saida_Priorizada", "Capacidade_ton_hora"],
                      title="Chegadas × Saídas × Capacidade", barmode="group")
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar: {e}")

else:
    st.info("Aguardando upload do CSV...")
    csv_exemplo = """Hora,Chegada_Ton,Saida_Priorizada,Equipe_Disponivel
04:00,5,0,2
05:00,15,0,2
06:00,0,10,2
07:00,0,0,2
08:00,0,5,2
09:00,0,0,2
10:00,3,0,0
11:00,0,3,1
12:00,0,0,1
13:00,0,0,1
14:00,2,0,1
15:00,10,5,2
16:00,0,0,2
17:00,0,8,2
18:00,4,0,0"""
    st.download_button("Baixar CSV de exemplo", csv_exemplo, "dados_logistica_exemplo.csv", "text/csv")
