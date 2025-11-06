import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(page_title="Capacidade x Produção", layout="wide")
st.title("📊 Capacidade x Produção")

# -----------------------------
# Entrada do fator dinâmico
# -----------------------------
st.sidebar.header("Configurações")
fator_dinamico = st.sidebar.number_input(
    "Fator Dinâmico (vol/kg)",
    min_value=0.0,
    value=16.10,
    step=0.1,
    format="%.2f"
)

st.write(f"**Fator atual:** {fator_dinamico:.2f}")

# -----------------------------
# Dados base de capacidade por hora
# -----------------------------
dados_capacidade = {
    "Hora": [
        "00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00",
        "08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00",
        "16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"
    ],
    "Capacidade": [
        552.1408578,552.1408578,552.1408578,552.1408578,953.1694808,953.1694808,
        1456.87693,1456.87693,1408.443521,552.1408578,48.43340858,904.7360722,
        1005.477562,1156.589797,300.2871332,300.2871332,199.5456433,300.2871332,
        1844.344199,1995.456433,2247.310158,2247.310158,1833.688849,121.0835214
    ]
}

df = pd.DataFrame(dados_capacidade)

# -----------------------------
# Cálculo da Capacidade Ajustada
# -----------------------------
df["Capacidade Ajustada"] = df["Capacidade"] * 1000 * fator_dinamico

# -----------------------------
# Produção simulada (ou real se tiver dataframe pronto)
# -----------------------------
# Aqui você pode substituir pela leitura do seu dataframe real
df["Produção"] = [3500000,3000000,3200000,2800000,4200000,4400000,4600000,4800000,
                  5100000,4900000,3800000,4000000,4200000,4400000,4600000,4800000,
                  4700000,4500000,4900000,5100000,5300000,5200000,4800000,4600000]

# -----------------------------
# Gráfico combinado
# -----------------------------
fig = go.Figure()

# Barras da produção
fig.add_trace(go.Bar(
    x=df["Hora"],
    y=df["Produção"],
    name="Produção",
    marker_color="red",
    yaxis="y1"
))

# Linha da capacidade ajustada
fig.add_trace(go.Scatter(
    x=df["Hora"],
    y=df["Capacidade Ajustada"],
    name="Capacidade Ajustada",
    mode="lines+markers",
    line=dict(color="purple", width=3),
    yaxis="y2"
))

# -----------------------------
# Layout do gráfico
# -----------------------------
fig.update_layout(
    title="Comparativo: Capacidade x Produção",
    xaxis=dict(title="Hora"),
    yaxis=dict(
        title="Produção (unidades)",
        side="left",
        showgrid=False,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="gray"
    ),
    yaxis2=dict(
        title="Capacidade Ajustada",
        overlaying="y",
        side="right",
        showgrid=False,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="gray"
    ),
    barmode="group",
    legend=dict(orientation="h", y=-0.2),
    template="plotly_white",
    height=600
)

# -----------------------------
# Exibição
# -----------------------------
st.plotly_chart(fig, use_container_width=True)

# Exibe tabela para conferência
with st.expander("📋 Ver dados detalhados"):
    st.dataframe(df.style.format({
        "Capacidade": "{:,.2f}",
        "Capacidade Ajustada": "{:,.2f}",
        "Produção": "{:,.0f}"
    }))
