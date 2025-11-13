# pages/Producao_x_Equipe_R1.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime, time, timedelta

st.set_page_config(layout="wide")
st.title("Produção vs Equipe Disponível – R1")

rotulos = st.checkbox("Rótulos", True)

# =============================================
# DADOS FIXOS
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
# FUNÇÕES AUXILIARES
# =============================================
def str_to_time(h):
    return datetime.strptime(h, "%H:%M").time()

def time_to_datetime(t):
    today = datetime.today().date()
    return datetime.combine(today, t)

# =============================================
# PROCESSAMENTO DOS DADOS
# =============================================
def extrair_producao(texto):
    cheg = {}; said = {}
    modo = None
    for l in texto.strip().split("\n"):
        l = l.strip()
        if l == "Cheg. Ton.": modo = "cheg"; continue
        if l == "Saida Ton.": modo = "said"; continue
        if not l: continue
        p = l.split()
        if len(p) < 2: continue
        h = p[0]
        try:
            v = float(p[1].replace(",", "."))
            if modo == "cheg":
                cheg[h] = cheg.get(h, 0) + v
            else:
                said[h] = said.get(h, 0) + v
        except: pass
    return cheg, said

cheg, said = extrair_producao(f"Cheg. Ton.\n{chegada_fixa}\nSaida Ton.\n{saida_fixa}")

# Criar lista completa de horários (de 00:00 até 23:45, de 15 em 15 min)
base_times = []
current = time(0, 0)
while current <= time(23, 45):
    base_times.append(current.strftime("%H:%M"))
    minutes = current.minute + 15
    hour_add = minutes // 60
    minutes = minutes % 60
    current = time(current.hour + hour_add, minutes)

# Adicionar todos os horários reais que existem nos dados
todos_horarios = set(base_times)
for h in cheg.keys(): todos_horarios.add(h)
for h in said.keys(): todos_horarios.add(h)

# Adicionar horários das jornadas
for text in [confer_fixa, aux_fixa]:
    for l in text.split("\n"):
        parts = l.strip().split()
        for p in parts[:-1]:
            if ":" in p and len(p) == 5:
                todos_horarios.add(p)

horarios_str = sorted(todos_horarios, key=str_to_time)
horarios_dt = [time_to_datetime(str_to_time(h, h) for h in horarios_str]

# Calcular equipe
def calcular_equipe(jornadas_list):
    eq = [0] * len(horarios_dt)
    for j in jornadas_list:
        e = str_to_time(j["e"])
        e_min = e.hour * 60 + e.minute
        if j["t"] == "c":
            si = str_to_time(j["si"])
            ri = str_to_time(j["ri"])
            sf = str_to_time(j["sf"])
            si_min = si.hour * 60 + si.minute
            ri_min = ri.hour * 60 + ri.minute
            sf_min = sf.hour * 60 + sf.minute
            for i, dt in enumerate(horarios_dt):
                t_min = dt.hour * 60 + dt.minute
                if (e_min <= t_min < si_min) or (ri_min <= t_min <= sf_min):
                    eq[i] += j["q"]
        else:
            sf = str_to_time(j["sf"])
            sf_min = sf.hour * 60 + sf.minute
            for i, dt in enumerate(horarios_dt):
                t_min = dt.hour * 60 + dt.minute
                if e_min <= t_min <= sf_min:
                    eq[i] += j["q"]
    return eq

# Processar jornadas
def processar_jornadas(texto):
    j = []
    for l in texto.strip().split("\n"):
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"t": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return j

eq_conf = calcular_equipe(processar_jornadas(confer_fixa))
eq_aux = calcular_equipe(processar_jornadas(aux_fixa))
eq_total = [a + b for a, b in zip(eq_conf, eq_aux)]

# Valores de produção
cheg_val = [round(cheg.get(h, 0), 1) for h in horarios_str]
said_val = [round(said.get(h, 0), 1) for h in horarios_str]

# DataFrame
df = pd.DataFrame({
    "Horario": horarios_dt,
    "Horario_Str": horarios_str,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq_total
})

# Escala equipe
max_ton = max(max(cheg_val), max(said_val), 1)
max_eq = max(eq_total, default=1)
scale = max_ton / max_eq * 0.9
df["Equipe_Escalada"] = df["Equipe"] * scale

# =============================================
# GRÁFICO
# =============================================
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#90EE90", opacity=0.8
))
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Saida_Ton"],
    name="Saída (ton)", marker_color="#E74C3C", opacity=0.8
))
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

if rotulos:
    for _, row in df.iterrows():
        if row["Chegada_Ton"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Chegada_Ton"], text=str(row["Chegada_Ton"]),
                               font=dict(size=9, color="green"), showarrow=False, yshift=10)
        if row["Saida_Ton"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Saida_Ton"], text=str(row["Saida_Ton"]),
                               font=dict(size=9, color="red"), showarrow=False, yshift=10)
        if row["Equipe">
            fig.add_annotation(x=row["Horario"], y=row["Equipe_Escalada"], text=str(int(row["Equipe"])),
                               font=dict(size=9, color="#9B59B6"), showarrow=False, yshift=8)

# EIXO X PERFEITO
fig.update_xaxes(
    title="Horário",
    type="date",
    tickformat="%H:%M",
    tickangle=0,
    tick0="2024-01-01 00:00",
    dtick=3600000,  # 1 hora
    minor=dict(dtick=900000, showgrid=True, gridcolor="rgba(0,0,0,0.1)")
)

fig.update_layout(
    height=650,
    barmode="stack",
    hovermode="x unified",
    legend=dict(x=0, y=1.1, orientation="h"),
    margin=dict(l=50, r=50, t=50, b=80)
)

st.plotly_chart(fig, use_container_width=True)

# Download
out = io.BytesIO()
df_export = df.copy()
df_export["Horario"] = df_export["Horario_Str"]
df_export = df_export[["Horario", "Chegada_Ton", "Saida_Ton", "Equipe"]]
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    df_export.to_excel(writer, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_r1.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
