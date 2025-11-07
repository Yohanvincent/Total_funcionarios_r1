# pages/Logistica_Real.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# CONFIGURAÇÃO
# =============================================
st.set_page_config(layout="wide", page_title="Logística + Funcionários (Inteiros)")
st.title("Logística + Produtividade (Funcionários 100% Inteiros)")

# =============================================
# CONFIGURAÇÕES DINÂMICAS
# =============================================
st.sidebar.header("Tempos de Operação (segundos)")
t_descarga = st.sidebar.number_input("Descarga (Auxiliar)", value=30, min_value=1)
t_carga = st.sidebar.number_input("Carga (Conferente)", value=28, min_value=1)

fator_kg_vol = st.sidebar.number_input("1 vol = ? kg", value=16.10, min_value=0.1, step=0.1, format="%.2f")

# Produtividade por pessoa (ton/h)
prod_descarga = (3600 / t_descarga) * fator_kg_vol / 1000  # ton/h por auxiliar
prod_carga = (3600 / t_carga) * fator_kg_vol / 1000        # ton/h por conferente

st.sidebar.markdown("### Produtividade por Pessoa")
st.sidebar.metric("Auxiliar (descarga)", f"{prod_descarga*1000:,.0f} kg/h")
st.sidebar.metric("Conferente (carga)", f"{prod_carga*1000:,.0f} kg/h")

rotulos = st.checkbox("Exibir rótulos", True)

# =============================================
# SESSION STATE
# =============================================
keys = ["chegadas_bytes", "saidas_bytes", "conf_bytes", "aux_bytes",
        "chegadas_name", "saidas_name", "conf_name", "aux_name"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None

# =============================================
# DADOS PADRÃO
# =============================================
padrao_chegadas = """00:00 1,7
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
20:30 3,2
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

padrao_saidas = """00:00 0,1
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

padrao_conf = """01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19
23:50 02:40 03:45 09:11 4"""

padrao_aux = """16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
19:00 22:52 12
19:00 23:00 00:05 04:09 13
19:15 23:06 1
21:00 01:00 02:05 06:08 29
21:30 01:30 02:30 06:33 1
22:00 02:00 03:05 07:03 20
23:30 03:30 04:35 08:49 25
23:50 02:40 03:45 09:11 1"""

# =============================================
# FUNÇÕES
# =============================================
def ler_bytes(b, fallback):
    if b is None: return fallback
    try: return b.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)

def min_hora(h):
    try: return sum(int(x) * (60 ** i) for i, x in enumerate(reversed(h.split(":"))))
    except: return 0

def extrair_movimentos(texto):
    d = {}
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) >= 2:
            h, v = p[0], p[1].replace(",", ".")
            try: d[h] = d.get(h, 0) + float(v)
            except: pass
    return d

def extrair_jornadas(texto):
    j = []
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({"e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"e": p[0], "sf": p[1], "q": int(p[2])})
    return j

# =============================================
# CARREGAR DADOS
# =============================================
chegadas_txt = ler_bytes(st.session_state.chegadas_bytes, padrao_chegadas)
saidas_txt   = ler_bytes(st.session_state.saidas_bytes,   padrao_saidas)
conf_txt     = ler_bytes(st.session_state.conf_bytes,     padrao_conf)
aux_txt      = ler_bytes(st.session_state.aux_bytes,      padrao_aux)

cheg = extrair_movimentos(chegadas_txt)
said = extrair_movimentos(saidas_txt)

# =============================================
# HORÁRIOS E FUNCIONÁRIOS (FORÇADO INTEIRO)
# =============================================
horas_set = set(cheg.keys()) | set(said.keys())
for txt in [conf_txt, aux_txt]:
    for l in txt.splitlines():
        p = l.split()
        if len(p) >= 4: horas_set.update(p[:4])
horarios = sorted(horas_set, key=min_hora)

timeline_min = [min_hora(h) for h in horarios]
conf_count = [0] * len(horarios)
aux_count = [0] * len(horarios)

def aplicar_jornada(j, tl, contador):
    e = min_hora(j["e"])
    sf = min_hora(j["sf"])
    if "si" in j:
        si = min_hora(j["si"])
        ri = min_hora(j["ri"])
        for i, t in enumerate(tl):
            if (e <= t < si) or (ri <= t <= sf):
                contador[i] += j["q"]
    else:
        for i, t in enumerate(tl):
            if e <= t <= sf:
                contador[i] += j["q"]

for j in extrair_jornadas(conf_txt): aplicar_jornada(j, timeline_min, conf_count)
for j in extrair_jornadas(aux_txt):   aplicar_jornada(j, timeline_min, aux_count)

# GARANTIR INTEIRO
conf_count = [int(x) for x in conf_count]
aux_count = [int(x) for x in aux_count]

# =============================================
# DATAFRAME
# =============================================
df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_ton": [round(cheg.get(h, 0), 1) for h in horarios],
    "Saida_ton": [round(said.get(h, 0), 1) for h in horarios],
    "Conferentes": conf_count,        # INTEIRO
    "Auxiliares": aux_count,          # INTEIRO
})

# Produtividade em ton/h
df["Prod_Conferentes_ton_h"] = (df["Conferentes"] * prod_carga).round(1)
df["Prod_Auxiliares_ton_h"] = (df["Auxiliares"] * prod_descarga).round(1)
df["Processamento_Total_ton_h"] = (df["Prod_Conferentes_ton_h"] + df["Prod_Auxiliares_ton_h"]).round(1)

# Acumulado real
acumulado = 0.0
acumulado_list = []
for _, row in df.iterrows():
    acumulado = max(0, acumulado + row["Chegada_ton"] - row["Saida_ton"])
    acumulado_list.append(round(acumulado, 1))
df["Acumulado_ton"] = acumulado_list

# =============================================
# GRÁFICO ÚNICO
# =============================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_ton"], name="Chegada", marker_color="#2ca02c"))
fig.add_trace(go.Bar(x=df["Horario"], y=-df["Saida_ton"], name="Saída", marker_color="#d62728"))

fig.add_trace(go.Scatter(x=df["Horario"], y=df["Acumulado_ton"], mode="lines", name="Acumulado",
                         fill="tozeroy", fillcolor="rgba(148,103,189,0.4)", line=dict(color="#9467bd", width=3)))

fig.add_trace(go.Scatter(x=df["Horario"], y=df["Processamento_Total_ton_h"], mode="lines", name="Processamento Total",
                         line=dict(color="#ff7f0e", width=3, dash="dash")))

fig.add_trace(go.Scatter(x=df["Horario"], y=df["Prod_Conferentes_ton_h"], mode="lines", name="Conferentes (ton/h)",
                         line=dict(color="#1f77b4", width=2)))
fig.add_trace(go.Scatter(x=df["Horario"], y=df["Prod_Auxiliares_ton_h"], mode="lines", name="Auxiliares (ton/h)",
                         line=dict(color="#006400", width=2)))

# Rótulos
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_ton"],
                               text=f"+{r['Chegada_ton']:.1f}", font=dict(color="white", size=9),
                               bgcolor="#2ca02c", showarrow=False, yshift=8)
        if r["Saida_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=-r["Saida_ton"],
                               text=f"-{r['Saida_ton']:.1f}", font=dict(color="white", size=9),
                               bgcolor="#d62728", showarrow=False, yshift=-8)

# Layout
max_y = max(df[["Chegada_ton", "Acumulado_ton", "Processamento_Total_ton_h", "Prod_Conferentes_ton_h", "Prod_Auxiliares_ton_h"]].max().max() * 1.2, 10)
min_y = -df["Saida_ton"].max() * 1.2

fig.update_layout(
    title="Logística + Produtividade (Funcionários 100% Inteiros)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas", range=[min_y, max_y]),
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=700,
    margin=dict(l=70, r=70, t=90, b=60),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# MÉTRICAS
# =============================================
st.markdown("### Métricas Operacionais")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chegada Total", f"{df['Chegada_ton'].sum():.1f} ton")
col2.metric("Saída Total", f"{df['Saida_ton'].sum():.1f} ton")
col3.metric("Acumulado Final", f"{df['Acumulado_ton'].iloc[-1]:.1f} ton")
col4.metric("Processamento Médio", f"{df['Processamento_Total_ton_h'].mean():.1f} ton/h")

# =============================================
# TABELA (INTEIRO FORÇADO)
# =============================================
with st.expander("Tabela Completa"):
    df_disp = df.copy()
    df_disp["Conferentes"] = df_disp["Conferentes"].astype(int)
    df_disp["Auxiliares"] = df_disp["Auxiliares"].astype(int)

    st.dataframe(df_disp.style.format({
        "Chegada_ton": "{:.1f}",
        "Saida_ton": "{:.1f}",
        "Acumulado_ton": "{:.1f}",
        "Processamento_Total_ton_h": "{:.1f}",
        "Prod_Conferentes_ton_h": "{:.1f}",
        "Prod_Auxiliares_ton_h": "{:.1f}",
        "Conferentes": "{:d}",   # INTEIRO
        "Auxiliares": "{:d}"     # INTEIRO
    }), use_container_width=True)

    # CSV com inteiros
    csv_df = df_disp.copy()
    csv_df["Conferentes"] = csv_df["Conferentes"].astype(int)
    csv_df["Auxiliares"] = csv_df["Auxiliares"].astype(int)
    csv = csv_df.to_csv(index=False).encode()
    st.download_button("Baixar CSV", csv, "logistica_inteiros.csv", "text/csv")
