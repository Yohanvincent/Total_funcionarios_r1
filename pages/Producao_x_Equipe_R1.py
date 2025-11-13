# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

st.set_page_config(layout="wide")
st.title("Produção vs Equipe Disponível")

rotulos = st.checkbox("Rótulos", True)

# =============================================
# DADOS FIXOS (NÃO EDITÁVEIS) - MANTIDOS 100%
# =============================================
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

# =============================================
# PROCESSAMENTO DOS DADOS (com todos os horários)
# =============================================
def extrair_producao():
    cheg = {}
    said = {}
    for linha in chegada_fixa.strip().splitlines():
        if not linha.strip(): continue
        p = linha.split(maxsplit=1)
        if len(p) < 2: continue
        h, v = p[0], p[1].replace(",", ".")
        cheg[h] = cheg.get(h, 0) + float(v)
    for linha in saida_fixa.strip().splitlines():
        if not linha.strip(): continue
        p = linha.split(maxsplit=1)
        if len(p) < 2: continue
        h, v = p[0], p[1].replace(",", ".")
        said[h] = said.get(h, 0) + float(v)
    return cheg, said

cheg, said = extrair_producao()

# Forçar todas as horas cheias + horários reais
horas_cheias = [f"{h:02d}:00" for h in range(24)]
todos_horarios = set(horas_cheias)
todos_horarios.update(cheg.keys())
todos_horarios.update(said.keys())

# Adicionar horários das jornadas
for texto in [confer_fixa, aux_fixa]:
    for palavra in texto.split():
        if ":" in palavra and len(palavra) == 5:
            todos_horarios.add(palavra)

horarios_str = sorted(todos_horarios, key=lambda x: int(x[:2])*60 + int(x[3:]))
base = datetime(2024, 1, 1)
horarios_dt = [base.replace(hour=int(h.split(":")[0]), minute=int(h.split(":")[1])) for h in horarios_str]

# Cálculo da equipe (mantido seu estilo)
def min_hora(h): return int(h[:2])*60 + int(h[3:])
def jornadas(t):
    j = []
    for l in t.strip().splitlines():
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"t": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return j

def calcular_equipe(jornadas_list):
    eq = [0] * len(horarios_dt)
    for j in jornadas_list:
        e = min_hora(j["e"])
        if j["t"] == "c":
            si = min_hora(j["si"])
            ri = min_hora(j["ri"])
            sf = min_hora(j["sf"])
            for i, t in enumerate([min_hora(h) for h in horarios_str]):
                if (e <= t < si) or (ri <= t <= sf):
                    eq[i] += j["q"]
        else:
            sf = min_hora(j["sf"])
            for i, t in enumerate([min_hora(h) for h in horarios_str]):
                if e <= t <= sf:
                    eq[i] += j["q"]
    return eq

j_conf = jornadas(confer_fixa)
j_aux = jornadas(aux_fixa)
eq_conf = calcular_equipe(j_conf)
eq_aux = calcular_equipe(j_aux)
eq_total = [c + a for c, a in zip(eq_conf, eq_aux)]

# DataFrame final
cheg_val = [round(cheg.get(h, 0), 1) for h in horarios_str]
said_val = [round(said.get(h, 0), 1) for h in horarios_str]

df = pd.DataFrame({
    "Horario": horarios_dt,
    "Horario_Str": horarios_str,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq_total
})

# Escala da equipe
max_ton = max(max(cheg_val), max(said_val), 1)
scale = max_ton / (max(eq_total) + 5) * 0.9
df["Equipe_Escalada"] = df["Equipe"] * scale

# =============================================
# GRÁFICO 100% COM SEU ESTILO + HORÁRIOS COMPLETOS
# =============================================
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#90EE90", opacity=0.85,
    width=1800000  # ← barras grossas!
))

fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Saida_Ton"],
    name="Saída (ton)", marker_color="#E74C3C", opacity=0.85,
    width=1800000
))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=9),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# Rótulos com borda (exatamente como você ama!)
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"{r['Chegada_Ton']}",
                               font=dict(color="#2ECC71", size=9), bgcolor="white", bordercolor="#90EE90", borderwidth=1,
                               showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"{r['Saida_Ton']}",
                               font=dict(color="#E74C3C", size=9), bgcolor="white", bordercolor="#E74C3C", borderwidth=1,
                               showarrow=False, yshift=10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"], text=f"{int(r['Equipe'])}",
                               font=dict(color="#9B59B6", size=10), bgcolor="white", bordercolor="#9B59B6", borderwidth=1,
                               showarrow=False, yshift=8)

# EIXO X: vertical, todos os horários, mesmo estilo
fig.update_xaxes(
    tickvals=df["Horario"],
    ticktext=df["Horario_Str"],
    tickangle=90,
    tickfont=dict(size=11),
    title="Horário"
)

fig.update_layout(
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", side="left", range=[0, max_ton + 10]),
    height=680,
    barmode="stack",
    hovermode="x unified",
    legend=dict(x=0, y=1.1, orientation="h"),
    margin=dict(l=60, r=60, t=40, b=110)
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# DOWNLOAD E DADOS FIXOS (igual ao seu)
# =============================================
out = io.BytesIO()
df_export = df[["Horario_Str", "Chegada_Ton", "Saida_Ton", "Equipe"]].copy()
df_export.columns = ["Horário", "Chegada_Ton", "Saída_Ton", "Equipe"]
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df_export.to_excel(w, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_vs_equipe.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("### Dados Fixos Utilizados")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Conferentes**")
    st.code(confer_fixa, language="text")
    st.markdown("**Produção - Chegada**")
    st.code(chegada_fixa, language="text")
with col2:
    st.markdown("**Auxiliares**")
    st.code(aux_fixa, language="text")
    st.markdown("**Produção - Saída**")
    st.code(saida_fixa, language="text")
