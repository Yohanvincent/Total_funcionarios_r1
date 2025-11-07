import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# -------------------------------------------------
# Configuração da página
# -------------------------------------------------
st.set_page_config(page_title="Análise de Toneladas Acumuladas", layout="wide")
st.title("📦 Análise de Toneladas Acumuladas no CD")

# -------------------------------------------------
# Dados de entrada (exemplo fornecido)
# -------------------------------------------------
chegadas_raw = """
00:00 1,7
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
23:20 8,2
"""

saidas_raw = """
00:00 0,1
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
23:30 0,6
"""

conferentes_raw = """
01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19
23:50 02:40 03:45 09:11 4
"""

auxiliares_raw = """
16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
19:00 22:52 12
19:00 23:00 00:05 04:09 13
19:15 23:06 1
21:00 01:00 02:05 06:08 29
21:30 01:30 02:30 06:33 1
22:00 02:00 03:05 07:03 20
23:30 03:30 04:35 08:49 25
23:50 02:40 03:45 09:11 1
"""

capacidade_raw = """
00:00 4.779
01:00 3.197
02:00 3.411
03:00 3.790
04:00 3.289
05:00 3.925
06:00 2.637
07:00 1.457
08:00 1.127
09:00 58
10:00 48
11:00 48
12:00 48
13:00 48
14:00 48
15:00 48
16:00 300
17:00 300
18:00 787
19:00 2.084
20:00 1.844
21:00 3.561
22:00 4.121
23:00 3.585
"""

# -------------------------------------------------
# Funções auxiliares
# -------------------------------------------------
def parse_time(s):
    return datetime.strptime(s, "%H:%M").replace(year=2025, month=1, day=1)

def parse_raw_movimentos(raw):
    linhas = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    data = []
    for linha in linhas:
        partes = linha.split()
        hora = partes[0]
        ton = float(partes[1].replace(',', '.'))
        data.append({"hora": parse_time(hora), "ton": ton})
    return pd.DataFrame(data)

def parse_raw_jornada(raw, tipo):
    linhas = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    data = []
    for linha in linhas:
        partes = linha.split()
        entrada = parse_time(partes[0])
        saida_intervalo = parse_time(partes[1])
        retorno_intervalo = parse_time(partes[2])
        saida_final = parse_time(partes[3])
        qtd = int(partes[4])
        for _ in range(qtd):
            data.append({
                "tipo": tipo,
                "entrada": entrada,
                "saida_intervalo": saida_intervalo,
                "retorno_intervalo": retorno_intervalo,
                "saida_final": saida_final
            })
    return pd.DataFrame(data)

def parse_capacidade(raw):
    linhas = [l.strip() for l in raw.strip().splitlines() if l.strip()]
    data = []
    for linha in linhas:
        partes = linha.split()
        hora = parse_time(partes[0])
        cap = float(partes[1].replace(',', '.').replace('.', '', partes[1].count('.')-1))
        data.append({"hora": hora, "capacidade": cap})
    return pd.DataFrame(data)

# -------------------------------------------------
# Carregamento dos dados
# -------------------------------------------------
df_chegadas = parse_raw_movimentos(chegadas_raw)
df_saidas   = parse_raw_movimentos(saidas_raw)
df_conf     = parse_raw_jornada(conferentes_raw, "Conferente")
df_aux      = parse_raw_jornada(auxiliares_raw, "Auxiliar")
df_cap      = parse_capacidade(capacidade_raw)

# -------------------------------------------------
# Parâmetros configuráveis (sidebar)
# -------------------------------------------------
st.sidebar.header("Parâmetros Operacionais")
tempo_desc = st.sidebar.number_input("Tempo descarregamento por pessoa (s)", value=30, min_value=1)
tempo_carr = st.sidebar.number_input("Tempo carregamento por pessoa (s)", value=38, min_value=1)
kg_por_vol = st.sidebar.number_input("Fator kg/vol (kg)", value=16.10, min_value=0.0)
kg_por_m3  = st.sidebar.number_input("1 m³ = kg", value=300.0, min_value=0.0)

# -------------------------------------------------
# Cálculo de funcionários por hora
# -------------------------------------------------
inicio = datetime(2025,1,1,0,0)
fim    = datetime(2025,1,2,0,0)
horas = pd.date_range(inicio, fim, freq='H')[:-1]

def funcionarios_por_hora(df_jornada):
    serie = pd.Series(0, index=horas)
    for _, row in df_jornada.iterrows():
        # intervalo de almoço
        periodos = [
            (row["entrada"], row["saida_intervalo"]),
            (row["retorno_intervalo"], row["saida_final"])
        ]
        for start, end in periodos:
            serie.loc[start:end] += 1
    return serie

func_conf = funcionarios_por_hora(df_conf)
func_aux  = funcionarios_por_hora(df_aux)
func_total = func_conf + func_aux

# -------------------------------------------------
# Cálculo de capacidade por hora (ton/h)
# -------------------------------------------------
# 3600 s/h
cap_desc = (3600 / tempo_desc) / 1000   # ton/h por pessoa (1 ton = 1000 kg)
cap_carr = (3600 / tempo_carr) / 1000   # ton/h por pessoa

# Supondo que conferentes descarregam e auxiliares carregam
capacidade_calc = (func_conf * cap_desc) + (func_aux * cap_carr)

# Mesclando com a capacidade informada (quando houver)
capacidade_final = pd.Series(0.0, index=horas)
for h in horas:
    mask = df_cap["hora"].apply(lambda x: x.time()) == h.time()
    if mask.any():
        capacidade_final[h] = df_cap.loc[mask, "capacidade"].iloc[0]
    else:
        capacidade_final[h] = capacidade_calc[h]

# -------------------------------------------------
# Acumulado de toneladas
# -------------------------------------------------
# Agregando chegadas e saídas por hora
chegadas_h = df_chegadas.groupby(df_chegadas["hora"].dt.floor('H'))["ton"].sum().reindex(horas, fill_value=0)
saidas_h   = df_saidas.groupby(df_saidas["hora"].dt.floor('H'))["ton"].sum().reindex(horas, fill_value=0)

acumulado = (chegadas_h - saidas_h).cumsum()

# -------------------------------------------------
# Gráfico 1 - Barras + Linhas (produção + funcionários + capacidade)
# -------------------------------------------------
fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# Barras
fig1.add_trace(go.Bar(
    x=horas,
    y=chegadas_h,
    name="Chegadas (ton)",
    marker_color="#2ca02c"
), secondary_y=False)

fig1.add_trace(go.Bar(
    x=horas,
    y=saidas_h,
    name="Saídas (ton)",
    marker_color="#d62728"
), secondary_y=False)

# Linhas
fig1.add_trace(go.Scatter(
    x=horas,
    y=func_total,
    mode='lines+markers',
    name="Funcionários Disponíveis",
    line=dict(color="#1f77b4", width=3)
), secondary_y=True)

fig1.add_trace(go.Scatter(
    x=horas,
    y=capacidade_final,
    mode='lines+markers',
    name="Capacidade (ton/h)",
    line=dict(color="#ff7f0e", width=3, dash='dash')
), secondary_y=True)

fig1.update_xaxes(title_text="Hora do Dia")
fig1.update_yaxes(title_text="Toneladas", secondary_y=False)
fig1.update_yaxes(title_text="Funcionários / Capacidade (ton/h)", secondary_y=True)
fig1.update_layout(
    title="Produção Horária + Recursos Disponíveis",
    barmode='stack',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=600
)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------
# Gráfico 2 - Acumulado de toneladas (linha com preenchimento)
# -------------------------------------------------
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=horas,
    y=acumulado,
    fill='tozeroy',
    mode='lines',
    name='Acumulado no Pátio',
    line=dict(color="#9467bd"),
    fillcolor="rgba(148,103,189,0.3)"
))

fig2.add_trace(go.Scatter(
    x=horas,
    y=chegadas_h.cumsum(),
    mode='lines',
    name='Total Chegadas (acum.)',
    line=dict(color="#2ca02c", dash='dot')
))

fig2.add_trace(go.Scatter(
    x=horas,
    y=saidas_h.cumsum(),
    mode='lines',
    name='Total Saídas (acum.)',
    line=dict(color="#d62728", dash='dot')
))

fig2.update_layout(
    title="Acumulado de Toneladas no Pátio (Chegada - Saída)",
    xaxis_title="Hora do Dia",
    yaxis_title="Toneladas",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# Resumo em tabela
# -------------------------------------------------
st.header("Resumo por Hora")
resumo = pd.DataFrame({
    "Hora": horas.strftime("%H:%M"),
    "Chegadas (ton)": chegadas_h.round(2).values,
    "Saídas (ton)": saidas_h.round(2).values,
    "Funcionários": func_total.values,
    "Capacidade (ton/h)": capacidade_final.round(2).values,
    "Acumulado (ton)": acumulado.round(2).values
})
st.dataframe(resumo, use_container_width=True)

# -------------------------------------------------
# Download dos dados
# -------------------------------------------------
csv = resumo.to_csv(index=False).encode()
st.download_button(
    label="📥 Baixar Resumo (CSV)",
    data=csv,
    file_name="resumo_acumulado_toneladas.csv",
    mime="text/csv"
)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption("Desenvolvido para **Tela_Inicial** – Streamlit + Plotly | Dados de exemplo do dia 01/01/2025")
