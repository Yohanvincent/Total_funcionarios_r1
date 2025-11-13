# pages/Producao_x_Equipe_R1.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
import io

st.set_page_config(layout="wide")
st.title("Produção vs Equipe Disponível – R1")

rotulos = st.checkbox("Rótulos", True)

# =============================================
# DADOS FIXOS (seus dados originais)
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
# FUNÇÕES
# =============================================
def str_to_minutes(h):
    hh, mm = map(int, h.split(":"))
    return hh * 60 + mm

def extrair_producao():
    cheg = {}
    said = {}
    for linha in chegada_fixa.split("\n"):
        if not linha.strip(): continue
        h, v = linha.split()[:2]
        cheg[h] = cheg.get(h, 0) + float(v.replace(",", "."))
    for linha in saida_fixa.split("\n"):
        if not linha.strip(): continue
        h, v = linha.split()[:2]
        said[h] = said.get(h, 0) + float(v.replace(",", "."))
    return cheg, said

cheg, said = extrair_producao()

# Todos os horários que existem (produção + jornadas)
horarios_set = set(cheg.keys()) | set(said.keys())
for texto in [confer_fixa, aux_fixa]:
    for palavra in texto.split():
        if ":" in palavra and len(palavra) == 5:
            horarios_set.add(palavra)

# Forçar todas as horas cheias
for h in range(24):
    hora = f"{h:02d}:00"
    horarios_set.add(hora)
    cheg[hora] = cheg.get(hora, 0)
    said[hora] = said.get(hora, 0)

horarios_str = sorted(horarios_set, key=str_to_minutes)

# Converter para datetime (só para o Plotly)
base_date = datetime(2024, 1, 1)
horarios_dt = [base_date.replace(hour=int(h.split(":")[0]), minute=int(h.split(":")[1])) for h in horarios_str]

# =============================================
# JORNADAS E EQUIPE
# =============================================
def processar_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        partes = linha.split()
        if len(partes) == 5 and partes[4].isdigit():
            jornadas.append({"e": partes[0], "si": partes[1], "ri": partes[2], "sf": partes[3], "q": int(partes[4])})
        elif len(partes) == 3 and partes[2].isdigit():
            jornadas.append({"e": partes[0], "sf": partes[1], "q": int(partes[2])})
    return jornadas

jornadas_conf = processar_jornadas(confer_fixa)
jornadas_aux = processar_jornadas(aux_fixa)

def calcular_equipe(jornadas):
    equipe = [0] * len(horarios_dt)
    for j in jornadas:
        entrada = str_to_minutes(j["e"])
        if "si" in j:  # jornada com intervalo
            saida_intervalo = str_to_minutes(j["si"])
            retorno = str_to_minutes(j["ri"])
            saida_final = str_to_minutes(j["sf"])
            for i, dt in enumerate(horarios_dt):
                t = dt.hour * 60 + dt.minute
                if (entrada <= t < saida_intervalo) or (retorno <= t <= saida_final):
                    equipe[i] += j["q"]
        else:
            saida_final = str_to_minutes(j["sf"])
            for i, dt in enumerate(horarios_dt):
                t = dt.hour * 60 + dt.minute
                if entrada <= t <= saida_final:
                    equipe[i] += j["q"]
    return equipe

eq_conf = calcular_equipe(jornadas_conf)
eq_aux = calcular_equipe(jornadas_aux)
eq_total = [a + b for a, b in zip(eq_conf, eq_aux)]

# =============================================
# DATAFRAME
# =============================================
df = pd.DataFrame({
    "Horario": horarios_dt,
    "Horario_Str": horarios_str,
    "Chegada": [round(cheg.get(h, 0), 1) for h in horarios_str],
    "Saida": [round(said.get(h, 0), 1) for h in horarios_str],
    "Equipe": eq_total
})

# Escala da linha de equipe
max_ton = max(df["Chegada"].max(), df["Saida"].max(), 1)
scale = max_ton / (df["Equipe"].max() + 5) * 0.9
df["Equipe_Esc"] = df["Equipe"] * scale

# =============================================
# GRÁFICO FINAL
# =============================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada"], name="Chegada (ton)", marker_color="#90EE90"))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida"], name="Saída (ton)", marker_color="#E74C3C"))
fig.add_trace(go.Scatter(x=df["Horario"], y=df["Equipe_Esc"], mode="lines+markers",
                         name="Equipe", line=dict(color="#9B59B6", width=4, dash="dot"),
                         customdata=df["Equipe"], hovertemplate="Equipe: %{customdata}"))

if rotulos:
    for _, row in df.iterrows():
        if row["Chegada"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Chegada"], text=str(row["Chegada"]),
                               font=dict(size=9), showarrow=False, yshift=10)
        if row["Saida"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Saida"], text=str(row["Saida"]),
                               font=dict(size=9, color="red"), showarrow=False, yshift=10)
        if row["Equipe"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Equipe_Esc"], text=str(int(row["Equipe"])),
                               font=dict(size=10, color="#9B59B6"), showarrow=False, yshift=8)

fig.update_xaxes(
    title="Horário",
    tickformat="%H:%M",
    dtick=3600000,  # 1 hora
    tickangle=0,
    minor=dict(dtick=900000, showgrid=True, gridcolor="lightgray")
)

fig.update_layout(height=650, barmode="stack", hovermode="x unified", legend=dict(x=0, y=1.1, orientation="h"))

st.plotly_chart(fig, use_container_width=True)

# =============================================
# DOWNLOAD
# =============================================
out = io.BytesIO()
df_export = df[["Horario_Str", "Chegada", "Saida", "Equipe"]].copy()
df_export.columns = ["Horário", "Chegada (ton)", "Saída (ton)", "Equipe"]
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    df_export.to_excel(writer, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_r1.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
