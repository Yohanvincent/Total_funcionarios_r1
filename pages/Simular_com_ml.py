import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import plotly.express as px
import io

st.set_page_config(page_title="Simular com ML", layout="wide")
st.title(" Simular Capacidade e Previsão com Machine Learning")

# =============== UPLOAD DO ARQUIVO ===============
uploaded_file = st.file_uploader(
    "Faça upload do seu CSV com os dados de carga e equipe",
    type=["csv"],
    help="O arquivo precisa ter pelo menos as colunas: Hora, Chegada_Ton, Saida_Priorizada, Equipe_Disponivel"
)

if uploaded_file is not None:
    try:
        # Correção: ler o arquivo corretamente no Streamlit Cloud
        df = pd.read_csv(uploaded_file)
        st.success("Arquivo carregado com sucesso!")
        st.dataframe(df.head(10))

        # =============== PRÉ-PROCESSAMENTO ===============
        # Converter Hora para minutos do dia
        df['Hora_dt'] = pd.to_datetime(df['Hora'], format='%H:%M', errors='coerce')
        df['Minutos_do_dia'] = df['Hora_dt'].dt.hour * 60 + df['Hora_dt'].dt.minute

        # Garantir que as colunas numéricas existam
        for col in ['Chegada_Ton', 'Saida_Priorizada', 'Equipe_Disponivel']:
            if col not in df.columns:
                st.error(f"Coluna obrigatória faltando: {col}")
                st.stop()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Cálculo da capacidade por hora (30s descarregar + 38s carregar ≈ 34s médio)
        ciclo_seg = 34
        ops_por_pessoa_por_hora = 3600 / ciclo_seg
        df['Capacidade_ton_hora'] = df['Equipe_Disponivel'] * ops_por_pessoa_por_hora

        # Acumulação de carga (simulação simples)
        df['Acumulação'] = (df['Chegada_Ton'].cumsum() - df['Saida_Priorizada'].cumsum()).clip(lower=0)

        # =============== MACHINE LEARNING ===============
        X = df[['Minutos_do_dia', 'Chegada_Ton', 'Equipe_Disponivel']]
        y = df['Acumulação']

        if len(df) < 5:
            st.warning("Poucos dados para treinar o modelo. Usando valores simulados.")
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)

            st.subheader(" Resultados do Modelo de Machine Learning")
            st.write(f"Erro Médio Absoluto (MAE): **{mae:.2f} toneladas**")

            # =============== PREVISÃO INTERATIVA ===============
            st.subheader(" Faça sua própria previsão")
            col1, col2, col3 = st.columns(3)
            with col1:
                hora_prev = st.time_input("Horário da previsão", value=pd.to_datetime("14:00").time())
            with col2:
                chegada_prev = st.number_input("Chegada de carga (ton)", min_value=0.0, value=5.0)
            with col3:
                equipe_prev = st.number_input("Equipe disponível", min_value=0, value=2, step=1)

            minutos = hora_prev.hour * 60 + hora_prev.minute
            previsao = model.predict([[minutos, chegada_prev, equipe_prev]])[0]

            st.success(f"Previsão de acumulação às {hora_prev.strftime('%H:%M')}: **{previsao:.2f} toneladas**")

        # =============== GRÁFICOS INTERATIVOS ===============
        st.subheader(" Visualizações")

        fig1 = px.line(df, x='Hora', y='Acumulação', title='Acumulação de Carga ao Longo do Dia',
                       markers=True, height=500)
        fig1.update_layout(xaxis_title="Horário", yaxis_title="Acumulação (ton)")
        st.write(fig1)

        fig2 = px.bar(df, x='Hora', y=['Chegada_Ton', 'Saida_Priorizada', 'Capacidade_ton_hora'],
                      title='Chegadas × Saídas × Capacidade por Hora',
                      barmode='group', height=500)
        st.write(fig2)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        st.info("Verifique se o CSV está no formato correto e tente novamente.")

else:
    st.info("Aguardando upload do arquivo CSV...")
    st.markdown("""
    ### Formato esperado do CSV (exemplo):
