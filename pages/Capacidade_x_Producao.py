import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Capacidade x Produção")

# --- Checkbox de rótulos ---
rotulos = st.checkbox("Exibir rótulos", True)

# --- Fator dinâmico (input lateral) ---
st.sidebar.header("Configurações")
fator_dinamico = st.sidebar.number_input(
    "Fator Dinâmico (vol/kg)",
    min_value=0.0,
    value=16.10,
    step=0.1,
    format="%.2f"
)

st.write(f"**Fator atual:** {fator_dinamico:.2f}")

# --- Dados base de capacidade ---
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

# --- Cálculo da capacidade ajustada ---
df["Capacidade Ajustada"] = (df["Capacidade"] * 1000 * fator_dinamico) / 1000  # converte para toneladas
df["Capacidade Ajustada"] = df["Capacidade Ajustada"].round(0)

# --- Simulação ou integração de produção real ---
# Aqui você pode substituir futuramente pelos dados reais vindos da aba Produção vs Equipe
df["Produção"] = [
    7, 6, 8, 5, 9, 10, 12, 15, 16, 13, 9, 10, 11, 12, 13, 15, 14, 13, 17, 18, 19, 18, 16, 14
]

# --- Gráfico ---
fig = go.Figure()

# Barras da produção (vermelhas)
fig.add_trace(go.Bar(
    x=df["Hora"], y=df["Produção"],
    name="Produção (ton)",
    marker_color="#E74C3C", opacity=0.85
))

# Linha da capacidade (roxa)
fig.add_trace(go.Scatter(
    x=df["Hora"], y=df["Capacidade Ajustada"],
    name="Capacidade (ton)",
    mode="lines+markers",
    line=dict(color="#9B59B6", width=4),
    marker=dict(size=7),
))

# --- Rótulos ---
if rotulos:
    for _, r in df.iterrows():
        if r["Produção"] > 0:
            fig.add_annotation(x=r["Hora"], y=r["Produção"],
                text=f"{int(r['Produção'])}",
                font=dict(color="#E74C3C", size=9),
                bgcolor="white", bordercolor="#E74C3C", borderwidth=1,
                showarrow=False, yshift=10)
        if r["Capacidade Ajustada"] > 0:
            fig.add_annotation(x=r["Hora"], y=r["Capacidade Ajustada"],
                text=f"{int(r['Capacidade Ajustada'])}",
                font=dict(color="#9B59B6", size=9),
                bgcolor="white", bordercolor="#9B59B6", borderwidth=1,
                showarrow=False, yshift=0)

# --- Layout do gráfico ---
max_y = max(df["Capacidade Ajustada"].max(), df["Produção"].max()) * 1.1

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

# --- Tabela expandida ---
with st.expander("📋 Ver dados detalhados"):
    st.dataframe(df.style.format({
        "Capacidade": "{:,.0f}",
        "Capacidade Ajustada": "{:,.0f}",
        "Produção": "{:,.0f}"
    }))
