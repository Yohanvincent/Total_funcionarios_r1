import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(layout="wide")
st.title("Capacidade x Produção Acumulada")

rotulos = st.checkbox("Exibir rótulos", True)

# Sidebar - Configurações
st.sidebar.header("Configurações")
fator_dinamico = st.sidebar.number_input(
    "Fator Dinâmico (vol/kg)",
    min_value=0.0,
    value=16.10,
    step=0.1,
    format="%.2f"
)
st.write(f"**Fator atual:** {fator_dinamico:.2f}")

# Upload opcional
uploaded_file = st.file_uploader("Carregar arquivo CSV (opcional)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, sep=";", decimal=",")
    df["Hora"] = pd.to_datetime(df["Hora"], format="%H:%M").dt.strftime("%H:%M")
else:
    # Dados base (sem upload)
    dados_capacidade = {
        "Hora": [
            "00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00",
            "08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00",
            "16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"
        ],
        "Capacidade_kg": [
            552.1408578,552.1408578,552.1408578,552.1408578,953.1694808,953.1694808,
            1456.87693,1456.87693,1408.443521,552.1408578,48.43340858,904.7360722,
            1005.477562,1156.589797,300.2871332,300.2871332,199.5456433,300.2871332,
            1844.344199,1995.456433,2247.310158,2247.310158,1833.688849,121.0835214
        ],
        "Produção (t)": [
            7, 6, 8, 5, 9, 10, 12, 15, 16, 13, 9, 10, 11, 12, 13, 15,
            14, 13, 17, 18, 19, 18, 16, 14
        ]
    }
    df = pd.DataFrame(dados_capacidade)

# Conversão para toneladas
df["Capacidade (t)"] = (df["Capacidade_kg"] * fator_dinamico) / 1000
df["Capacidade (t)"] = df["Capacidade (t)"].round(1)

# Interpolação da capacidade — mantém valor constante até o próximo horário
df_capacidade = pd.DataFrame({
    "Hora": pd.date_range("00:00", "23:59", freq="15min").strftime("%H:%M")
})
df_capacidade = pd.merge_asof(
    df_capacidade.sort_values("Hora").assign(Hora=pd.to_datetime(df_capacidade["Hora"], format="%H:%M")),
    df.assign(Hora=pd.to_datetime(df["Hora"], format="%H:%M")).sort_values("Hora")[["Hora", "Capacidade (t)"]],
    on="Hora",
    direction="backward"
)
df_capacidade["Hora"] = df_capacidade["Hora"].dt.strftime("%H:%M")

# Gráfico
fig = go.Figure()

# Barras (Produção)
fig.add_trace(go.Bar(
    x=df["Hora"], y=df["Produção (t)"],
    name="Produção (t)",
    marker_color="#90EE90", opacity=0.85
))

# Linha (Capacidade)
fig.add_trace(go.Scatter(
    x=df_capacidade["Hora"], y=df_capacidade["Capacidade (t)"],
    name="Capacidade (t)",
    mode="lines",
    line=dict(color="#9B59B6", width=4)
))

# Rótulos
if rotulos:
    for _, r in df.iterrows():
        fig.add_annotation(
            x=r["Hora"], y=r["Produção (t)"],
            text=f"{r['Produção (t)']:.1f}",
            font=dict(color="#90EE90", size=9),
            bgcolor="white", bordercolor="#90EE90", borderwidth=1,
            showarrow=False, yshift=10
        )
        fig.add_annotation(
            x=r["Hora"], y=r["Capacidade (t)"],
            text=f"{r['Capacidade (t)']:.1f}",
            font=dict(color="#9B59B6", size=9),
            bgcolor="white", bordercolor="#9B59B6", borderwidth=1,
            showarrow=False, yshift=0
        )

# Layout
max_y = max(df["Capacidade (t)"].max(), df["Produção (t)"].max()) * 1.1

fig.update_layout(
    xaxis_title="Hora",
    yaxis=dict(title="Toneladas", range=[0, max_y]),
    height=650,
    hovermode="x unified",
    legend=dict(x=0, y=1.1, orientation="h"),
    barmode="group",
    margin=dict(l=60, r=60, t=40, b=60),
    plot_bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)

# Dados detalhados
with st.expander("📋 Ver dados detalhados"):
    st.dataframe(df.style.format({
        "Capacidade_kg": "{:,.1f}",
        "Capacidade (t)": "{:,.1f}",
        "Produção (t)": "{:,.1f}"
    }))
