# pages/Acumulado_x_Producao.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import timedelta, datetime
import io

st.set_page_config(layout="wide")
st.title("Acumulado x Produção")

# ======================
# CONFIGURAÇÕES
# ======================
st.sidebar.header("Configurações")
fator_dinamico = st.sidebar.number_input("Fator Dinâmico (vol/kg)", value=16.10, step=0.1)
tempo_descarga = st.sidebar.number_input("Tempo de descarga por pessoa (segundos)", value=30)
densidade = 300  # 1 m³ = 300 kg

# ======================
# DADOS DE PRODUÇÃO (padrão)
# ======================
dados_producao = {
    "00:00": 7.3,
    "00:30": 8.1,
    "01:00": 6.9,
    "01:30": 5.8,
    "02:00": 4.0,
    "02:30": 6.9,
    "03:00": 3.1,
    "04:00": 5.0,
    "05:00": 8.0,
    "06:00": 10.0,
    "07:00": 12.0,
    "08:00": 14.0,
    "09:00": 8.0,
    "10:00": 6.0,
    "11:00": 5.0,
    "12:00": 7.0,
    "13:00": 8.0,
    "14:00": 9.0,
    "15:00": 5.0,
    "16:00": 3.0,
    "17:00": 7.0,
    "18:00": 9.0,
    "19:00": 6.0,
    "20:00": 8.0,
    "21:00": 10.0,
    "22:00": 5.0,
    "23:00": 3.0,
}

df_prod = pd.DataFrame(list(dados_producao.items()), columns=["Hora", "Producao_ton"])
df_prod["Hora"] = pd.to_datetime(df_prod["Hora"], format="%H:%M")

# ======================
# DADOS DE FUNCIONÁRIOS (padrão)
# ======================
dados_func = {
    "00:00": 9,
    "04:00": 27,
    "06:00": 1,
    "07:45": 1,
    "08:00": 2,
    "10:00": 11,
    "12:00": 8,
    "13:00": 5,
    "15:45": 7,
    "16:30": 2,
    "18:00": 19,
    "19:00": 5,
    "23:00": 2,
}
df_func = pd.DataFrame(list(dados_func.items()), columns=["Hora", "Funcionarios"])
df_func["Hora"] = pd.to_datetime(df_func["Hora"], format="%H:%M")

# interpolar horários
hora_inicio = pd.to_datetime("00:00", format="%H:%M")
hora_fim = pd.to_datetime("23:59", format="%H:%M")
intervalos = pd.date_range(hora_inicio, hora_fim, freq="15min")

df_func_interp = pd.DataFrame({"Hora": intervalos})
df_func_interp["Funcionarios"] = np.interp(
    df_func_interp["Hora"].astype(np.int64),
    df_func["Hora"].astype(np.int64),
    df_func["Funcionarios"]
)

# ======================
# CÁLCULO DE ACUMULADO
# ======================
df = pd.merge_asof(df_prod.sort_values("Hora"), df_func_interp.sort_values("Hora"),
                   on="Hora", direction="nearest")

df["Capacidade_saida_ton_h"] = (df["Funcionarios"] * (3600 / tempo_descarga) *
                                (fator_dinamico / 1000) * densidade / 1000)

estoque = []
acumulado = 0

for i, row in df.iterrows():
    acumulado += row["Producao_ton"]
    acumulado -= row["Capacidade_saida_ton_h"] / 4  # fração (15 min = 1/4h)
    if acumulado < 0:
        acumulado = 0
    estoque.append(acumulado)

df["Estoque_ton"] = estoque

# ======================
# GRÁFICO
# ======================
fig = go.Figure()

# Barras - Produção pontual
fig.add_trace(go.Bar(
    x=df["Hora"], y=df["Producao_ton"],
    name="Produção (Pontual)",
    marker_color="rgba(150,100,255,0.6)",
    yaxis="y1"
))

# Linha - Estoque acumulado
fig.add_trace(go.Scatter(
    x=df["Hora"], y=df["Estoque_ton"],
    mode="lines+markers",
    name="Estoque Real (Acumulado)",
    line=dict(color="lime", width=3),
    fill="tozeroy",
    yaxis="y1"
))

# Linha - Funcionários (eixo secundário)
fig.add_trace(go.Scatter(
    x=df["Hora"], y=df["Funcionarios"],
    mode="lines+markers",
    name="Total de Funcionários",
    line=dict(color="royalblue", width=2, dash="dot"),
    yaxis="y2"
))

# Layout
fig.update_layout(
    height=600,
    hovermode="x unified",
    bargap=0.05,
    plot_bgcolor="#0f1117",
    paper_bgcolor="#0f1117",
    font=dict(color="white", size=13),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(0,0,0,0)"
    ),
    xaxis=dict(
        title="Horário",
        tickformat="%H:%M",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.1)"
    ),
    yaxis=dict(
        title="Toneladas",
        showgrid=True,
        gridcolor="rgba(255,255,255,0.1)"
    ),
    yaxis2=dict(
        title="Funcionários",
        overlaying="y",
        side="right",
        showgrid=False
    )
)

st.plotly_chart(fig, use_container_width=True)

# Mostrar dados brutos
with st.expander("Ver tabela de dados"):
    st.dataframe(df)
