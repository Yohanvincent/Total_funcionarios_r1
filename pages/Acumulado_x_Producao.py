# pages/Acumulado_x_Producao.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# CONFIGURAÇÃO
# =============================================
st.set_page_config(layout="wide")
st.title("📦 Capacidade x Produção x Acumulado x Funcionários")

rotulos = st.checkbox("Exibir rótulos", True)

# =============================================
# SESSION STATE
# =============================================
keys = ["chegadas_bytes", "saidas_bytes", "conf_bytes", "aux_bytes", "capacidade_bytes",
        "chegadas_name", "saidas_name", "conf_name", "aux_name", "capacidade_name"]
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

padrao_capacidade = """00:00 4.779
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
23:00 3.585"""

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
    data = {}
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) >= 2:
            h, v = p[0], p[1].replace(",", ".")
            try: data[h] = data.get(h, 0) + float(v)
            except: pass
    return data

def extrair_jornadas(texto):
    jornadas = []
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            jornadas.append({"e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            jornadas.append({"e": p[0], "sf": p[1], "q": int(p[2])})
    return jornadas

def extrair_capacidade(texto):
    cap = {}
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) >= 2:
            h, v = p[0], p[1].replace(",", ".")
            try: cap[h] = float(v)
            except: pass
    return cap

def floor_hour(h):
    hh = str(min_hora(h) // 60).zfill(2)
    return f"{hh}:00"

# =============================================
# CARREGAR DADOS
# =============================================
chegadas_txt = ler_bytes(st.session_state.chegadas_bytes, padrao_chegadas)
saidas_txt   = ler_bytes(st.session_state.saidas_bytes, padrao_saidas)
conf_txt     = ler_bytes(st.session_state.conf_bytes, padrao_conf)
aux_txt      = ler_bytes(st.session_state.aux_bytes, padrao_aux)
cap_txt      = ler_bytes(st.session_state.capacidade_bytes, padrao_capacidade)

cheg = extrair_movimentos(chegadas_txt)
said = extrair_movimentos(saidas_txt)
capacidade_hora = extrair_capacidade(cap_txt)

# =============================================
# TODAS AS HORAS ÚNICAS
# =============================================
horas_set = set(cheg.keys()) | set(said.keys()) | set(capacidade_hora.keys())
for texto in [conf_txt, aux_txt]:
    for l in texto.splitlines():
        p = l.split()
        if len(p) >= 4: horas_set.update(p[:4])
horarios = sorted(horas_set, key=min_hora)

# =============================================
# FUNCIONÁRIOS POR HORÁRIO
# =============================================
timeline_min = [min_hora(h) for h in horarios]
func_total = [0] * len(horarios)

def aplicar_jornada(j, tl):
    e = min_hora(j["e"])
    sf = min_hora(j["sf"])
    if "si" in j:
        si = min_hora(j["si"])
        ri = min_hora(j["ri"])
        for i, t in enumerate(tl):
            if (e <= t < si) or (ri <= t <= sf):
                func_total[i] += j["q"]
    else:
        for i, t in enumerate(tl):
            if e <= t <= sf:
                func_total[i] += j["q"]

for j in extrair_jornadas(conf_txt): aplicar_jornada(j, timeline_min)
for j in extrair_jornadas(aux_txt):   aplicar_jornada(j, timeline_min)

# =============================================
# DATAFRAME FINAL (TONELADAS)
# =============================================
df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_ton": [round(cheg.get(h, 0), 2) for h in horarios],
    "Saida_ton": [round(said.get(h, 0), 2) for h in horarios],
    "Funcionarios": func_total,
    "Capacidade_ton": [round(capacidade_hora.get(floor_hour(h), 0), 3) for h in horarios],
})

df["Acumulado_ton"] = (df["Chegada_ton"] - df["Saida_ton"]).cumsum()

# =============================================
# GRÁFICO: TUDO EM TONELADAS + FUNCIONÁRIOS
# =============================================
fig = go.Figure()

# Barras empilhadas
fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_ton"], name="Chegada (ton)", marker_color="#2ca02c"))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_ton"], name="Saída (ton)", marker_color="#d62728"))

# Capacidade (degrau)
x_step, y_step = [], []
for i, row in df.iterrows():
    x_step.append(row["Horario"])
    y_step.append(row["Capacidade_ton"])
    if i < len(df) - 1:
        x_step.extend([row["Horario"], df.iloc[i+1]["Horario"]])
        y_step.extend([row["Capacidade_ton"], row["Capacidade_ton"]])

fig.add_trace(go.Scatter(
    x=x_step, y=y_step, mode="lines", name="Capacidade (ton)",
    line=dict(color="#9B59B6", width=4), hovertemplate="%{y:.3f} ton"
))

# Acumulado (linha com área)
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Acumulado_ton"],
    mode="lines", name="Acumulado (ton)", fill="tozeroy",
    fillcolor="rgba(148, 103, 189, 0.3)", line=dict(color="#9467bd", width=3),
    hovertemplate="%{y:.2f} ton"
))

# Funcionários (linha com área - escala à direita)
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Funcionarios"],
    mode="lines", name="Funcionários", yaxis="y2",
    fill="tozeroy", fillcolor="rgba(30, 144, 255, 0.2)",
    line=dict(color="#1f77b4", width=3), hovertemplate="%{y} pessoas"
))

# Rótulos
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_ton"], text=f"{r['Chegada_ton']:.1f}",
                               font=dict(color="white", size=9), bgcolor="#2ca02c", showarrow=False, yshift=8)
        if r["Saida_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=r["Saida_ton"], text=f"{r['Saida_ton']:.1f}",
                               font=dict(color="white", size=9), bgcolor="#d62728", showarrow=False, yshift=8)

# Layout com eixo duplo (só para funcionários)
max_ton = max(df["Capacidade_ton"].max(), df["Acumulado_ton"].max(), 10) * 1.15
max_func = df["Funcionarios"].max() * 1.3

fig.update_layout(
    title="Análise Unificada (Toneladas + Funcionários)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas", range=[0, max_ton]),
    yaxis2=dict(title="Funcionários", overlaying="y", side="right", range=[0, max_func]),
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=700,
    margin=dict(l=70, r=80, t=80, b=60)
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# UPLOADS
# =============================================
st.markdown("### Upload de Arquivos")
cols = st.columns(5)
with cols[0]:
    up = st.file_uploader("Chegadas", ["txt","csv","xlsx"], key="c")
    if up: st.session_state.chegadas_bytes, st.session_state.chegadas_name = up.getvalue(), up.name
    if st.session_state.chegadas_name: st.success(st.session_state.chegadas_name)
with cols[1]:
    up = st.file_uploader("Saídas", ["txt","csv","xlsx"], key="s")
    if up: st.session_state.saidas_bytes, st.session_state.saidas_name = up.getvalue(), up.name
    if st.session_state.saidas_name: st.success(st.session_state.saidas_name)
with cols[2]:
    up = st.file_uploader("Conferentes", ["txt","csv","xlsx"], key="conf")
    if up: st.session_state.conf_bytes, st.session_state.conf_name = up.getvalue(), up.name
    if st.session_state.conf_name: st.success(st.session_state.conf_name)
with cols[3]:
    up = st.file_uploader("Auxiliares", ["txt","csv","xlsx"], key="aux")
    if up: st.session_state.aux_bytes, st.session_state.aux_name = up.getvalue(), up.name
    if st.session_state.aux_name: st.success(st.session_state.aux_name)
with cols[4]:
    up = st.file_uploader("Capacidade", ["txt","csv","xlsx"], key="cap")
    if up: st.session_state.capacidade_bytes, st.session_state.capacidade_name = up.getvalue(), up.name
    if st.session_state.capacidade_name: st.success(st.session_state.capacidade_name)

# =============================================
# TABELA
# =============================================
with st.expander("Dados Completos"):
    st.dataframe(df.style.format({
        "Chegada_ton": "{:.2f}", "Saida_ton": "{:.2f}",
        "Acumulado_ton": "{:.2f}", "Capacidade_ton": "{:.3f}",
        "Funcionarios": "{:.0f}"
    }), use_container_width=True)

    csv = df.to_csv(index=False).encode()
    st.download_button("Baixar CSV", csv, "dados_unificados.csv", "text/csv")
