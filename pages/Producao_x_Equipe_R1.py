# Producao_x_Equipe_R1.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# -------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------
st.set_page_config(page_title="Logística – Produção vs Equipe R1", layout="wide")

# -------------------------------------------------
# FUNÇÃO AUXILIAR: string → datetime (data fixa 2025-11-12)
# -------------------------------------------------
def hora_to_datetime(hora_str: str, data_base: str = "2025-11-12") -> datetime:
    h = datetime.strptime(hora_str, "%H:%M").time()
    return datetime.combine(datetime.strptime(data_base, "%Y-%m-%d").date(), h)

# -------------------------------------------------
# DADOS FIXOS (100% ORIGINAIS – NÃO EDITÁVEIS)
# -------------------------------------------------
chegada_fixa = """00:00 1,7
00:00 6,3
00:20 14,9
00:30 2,6
01:15 3,9
01:30 7,3
01:30 14,8
01:50 1,8
02:10 2,8
02:25 10,2
02:30 8,9
03:00 9,6
03:00 32,7
03:00 7,9
03:15 6,5
03:30 15,7
03:30 8,9
03:30 4,4
03:45 3,8
04:00 16,4
04:00 8,2
04:05 0,1
04:15 4,2
04:20 8,7
04:20 5,7
04:30 8,2
04:30 6,9
04:30 9,7
04:40 0,0
04:45 9,2
04:45 6,1
04:45 15,3
04:45 11,4
04:50 10,4
05:00 4,2
05:00 5,0
05:10 13,1
05:15 7,5
05:20 0,0
05:25 6,6
05:30 15,8
05:40 3,3
06:00 8,0
06:00 4,3
06:10 0,0
06:10 0,0
07:00 1,7
08:00 10,2
10:20 8,0
10:30 0,0
11:00 0,0
11:45 0,0
11:55 3,3
12:05 9,0
14:10 0,0
14:45 0,0
15:30 0,0
16:15 9,4
16:25 0,0
16:30 10,0
20:00 5,2
20:00 5,6
20:00 2,4
20:15 5,0
20:15 12,4
20:15 4,4
20:30 3,5
20:45 1,1
20:45 4,9
21:00 3,6
21:00 6,1
21:10 6,6
21:15 6,6
21:25 7,5
21:30 4,6
21:30 3,9
21:30 0,8
21:30 5,4
21:40 9,2
21:40 9,1
21:40 2,2
21:40 6,9
21:45 0,0
22:00 1,1
22:00 8,0
22:30 13,5
22:30 3,8
22:30 3,7
22:45 1,8
22:45 7,3
23:00 2,6
23:15 1,4
23:20 8,2"""

saida_fixa = """00:00 0,1
00:30 1,4
00:30 1,3
00:45 6,1
01:00 2,2
01:00 2,2
01:20 2,0
01:30 3,8
01:45 5,2
02:00 0,7
02:00 2,1
02:00 0,6
02:30 12,8
02:40 3,2
03:15 4,4
03:20 17,1
03:30 0,5
03:30 0,7
03:45 3,4
04:00 3,2
04:00 5,9
04:00 12,4
04:00 7,5
04:10 6,1
04:15 7,0
04:40 0,4
04:40 0,8
05:00 13,0
05:00 6,5
05:00 5,1
05:00 8,0
05:00 12,4
05:00 7,5
05:00 0,0
05:00 7,2
05:00 15,2
05:00 15,7
05:40 8,0
06:00 14,4
06:00 10,4
06:00 16,3
06:00 14,2
06:00 13,8
06:10 5,8
06:30 8,2
06:30 3,9
06:30 5,4
06:30 10,3
06:30 7,6
07:00 3,7
07:00 15,9
07:00 4,2
07:00 3,3
07:00 0,8
07:00 0,0
07:00 9,7
07:00 3,6
07:00 4,9
07:00 4,6
07:00 13,1
07:00 15,6
07:00 11,4
07:00 9,0
07:00 5,7
07:10 5,7
07:10 7,7
07:15 14,9
07:45 4,7
08:45 3,1
11:00 5,4
17:15 3,1
21:30 14,6
22:00 6,4
22:00 2,7
22:20 17,2
22:30 1,8
22:30 3,1
22:30 1,1
22:30 1,4
22:30 1,5
22:30 6,4
22:40 6,2
23:00 1,7
23:00 0,1
23:15 4,9
23:30 2,3
23:30 1,1
23:30 2,2
23:30 7,9
23:30 1,8
23:30 0,0
23:30 0,3
23:30 0,6"""

confer_fixa = """01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19
23:50 02:40 03:45 09:11 4"""

aux_fixa = """16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
19:00 22:52 12
19:00 23:00 00:05 04:09 13
19:15 23:06 1
21:00 01:00 02:05 06:08 29
21:30 01:30 02:30 06:33 1
22:00 02:00 03:05 07:03 20
23:30 03:30 04:35 08:49 25
23:50 02:40 03:45 09:11 1"""

# -------------------------------------------------
# PARSE DOS DADOS
# -------------------------------------------------
def parse_producao(texto: str) -> pd.DataFrame:
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    rows = []
    for linha in linhas:
        partes = linha.split()
        hora = partes[0]
        valor = float(partes[1].replace(",", "."))
        rows.append({"hora": hora_to_datetime(hora), "valor": valor})
    df = pd.DataFrame(rows)
    # Agrupar por hora e somar (evita duplicatas)
    df = df.groupby("hora")["valor"].sum().reset_index()
    return df

def parse_equipe(texto: str) -> pd.DataFrame:
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    rows = []
    for linha in linhas:
        partes = linha.split()
        if len(partes) == 3:
            inicio, fim, qtd_str = partes
            qtd = int(qtd_str)
        else:
            inicio, fim, _, _, qtd_str = partes[:5]
            qtd = int(qtd_str)

        start = hora_to_datetime(inicio)
        end = hora_to_datetime(fim)
        cur = start
        while cur <= end:
            rows.append({"hora": cur, "disponivel": qtd})
            cur += timedelta(hours=1)
    df = pd.DataFrame(rows)
    # Somar equipe por hora (evita duplicatas)
    df = df.groupby("hora")["disponivel"].sum().reset_index()
    return df

# -------------------------------------------------
# CÁLCULO FINAL
# -------------------------------------------------
@st.cache_data
def calcular_dados():
    # ---- produção (chegada - saída) ----
    df_chegada = parse_producao(chegada_fixa)
    df_saida   = parse_producao(saida_fixa)

    df_chegada["movimento"] = df_chegada["valor"]
    df_saida["movimento"]   = -df_saida["valor"]

    df_mov = pd.concat([df_chegada, df_saida], ignore_index=True)
    df_mov = df_mov.groupby("hora")["movimento"].sum().reset_index()
    df_mov = df_mov.sort_values("hora")
    df_mov["acumulado"] = df_mov["movimento"].cumsum()

    # ---- equipe (conferentes + auxiliares) ----
    df_confer = parse_equipe(confer_fixa)
    df_aux    = parse_equipe(aux_fixa)
    df_equipe = pd.concat([df_confer, df_aux], ignore_index=True)
    df_equipe = df_equipe.groupby("hora")["disponivel"].sum().reset_index()

    return df_mov[["hora", "acumulado"]], df_equipe

# -------------------------------------------------
# PREPARAÇÃO PARA GRÁFICO HOURLY (00:00–23:00)
# -------------------------------------------------
def preparar_hourly(df, col, start, end):
    hourly = pd.date_range(start, end, freq="1H")
    df_h = df.set_index("hora").reindex(hourly).reset_index()
    df_h[col] = df_h[col].fillna(0)
    df_h.columns = ["hora", col]
    return df_h

# -------------------------------------------------
# INTERFACE
# -------------------------------------------------
st.title("Produção vs Equipe Disponível – R1")

acumulado, equipe = calcular_dados()

start_day = datetime(2025, 11, 12, 0, 0)
end_day   = datetime(2025, 11, 12, 23, 0)

# Preparar dados hourly
acum_h = preparar_hourly(acumulado, "acumulado", start_day, end_day)
equipe_h = preparar_hourly(equipe, "disponivel", start_day, end_day)

# ---------- GRÁFICO ----------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=equipe_h["hora"],
        y=equipe_h["disponivel"],
        mode="lines+markers",
        name="Equipe Disponível",
        line=dict(color="#1f77b4", width=2),
        marker=dict(size=6),
    )
)

fig.add_trace(
    go.Scatter(
        x=acum_h["hora"],
        y=acum_h["acumulado"],
        mode="lines+markers",
        name="Acumulação Líquida (t)",
        line=dict(color="#2ca02c", width=2),
        marker=dict(size=6),
    )
)

# Eixo X: 1h em 1h + grade fina
fig.update_xaxes(
    title="Hora do Dia",
    type="date",
    tickformat="%H:%M",
    tickmode="linear",
    dtick=3600 * 1000,
    range=[start_day, end_day],
    minor=dict(
        tickmode="linear",
        dtick=300 * 1000,
        showgrid=True,
        gridcolor="lightgray",
    ),
)

fig.update_yaxes(title="Quantidade")
fig.update_layout(
    title="Produção vs Equipe Disponível – R1",
    hovermode="x unified",
    xaxis_rangeslider_visible=True,
    height=650,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
)

st.plotly_chart(fig, use_container_width=True)

# ---------- RENOMEAR EIXOS ----------
with st.expander("Renomear eixos (opcional)"):
    col1, col2 = st.columns(2)
    with col1:
        novo_x = st.text_input("Título eixo X", value="Hora do Dia")
    with col2:
        novo_y = st.text_input("Título eixo Y", value="Quantidade")
    if st.button("Aplicar"):
        fig.update_xaxes(title=novo_x)
        fig.update_yaxes(title=novo_y)
        st.plotly_chart(fig, use_container_width=True)

st.caption(
    "• **Dados 100% originais** – duplicatas somadas\n"
    "• **Eixo X**: 1h em 1h + grade fina (5 min)\n"
    "• **Dia completo**: 00:00 a 23:00"
)
