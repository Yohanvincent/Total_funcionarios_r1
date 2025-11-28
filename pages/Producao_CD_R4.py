import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="Produção × Equipe - CD")
st.title("Produção × Equipe CD – Chegada / Saída / Equipe")

# =============== SESSION STATE ===============
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.chegada = """00:00 15,5
03:30 9,6
04:20 5,9
12:30 10,5"""

    st.session_state.saida = """21:00 8,5
21:30 12,3
22:00 7,8"""

    st.session_state.conferente = """01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19
23:50 02:40 03:45 09:11 4"""

    st.session_state.auxiliar = """16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
19:00 22:52 12
19:00 23:00 00:05 04:09 13
19:15 23:06 1
21:00 01:00 02:05 06:08 29
21:30 01:30 02:30 06:33 1
22:00 02:00 03:05 07:03 20
23:30 03:30 04:35 08:49 25
23:50 02:40 03:45 09:11 1"""

    st.session_state.rotulos = True


# =============== FUNÇÕES AUXILIARES ===============
def hora_para_minutos(hora_str):
    try:
        h, m = map(int, hora_str.split(":"))
        return h * 60 + m
    except:
        return 0

def todos_horarios():
    horarios = set()
    textos = [
        st.session_state.chegada,
        st.session_state.saida,
        st.session_state.conferente,
        st.session_state.auxiliar
    ]
    for texto in textos:
        for linha in texto.strip().split("\n"):
            if not linha.strip():
                continue
            horarios.add(linha.split()[0])
    return sorted(horarios, key=hora_para_minutos)

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        p = linha.split()
        if len(p) == 5 and p[4].isdigit():
            jornadas.append({
                "tipo": "completa",
                "e": hora_para_minutos(p[0]),
                "si": hora_para_minutos(p[1]),
                "ri": hora_para_minutos(p[2]),
                "sf": hora_para_minutos(p[3]),
                "qtd": int(p[4])
            })
        elif len(p) == 3 and p[2].isdigit():
            jornadas.append({
                "tipo": "simples",
                "e": hora_para_minutos(p[0]),
                "sf": hora_para_minutos(p[1]),
                "qtd": int(p[2])
            })
    return jornadas

def calcular_equipe(horarios_str, jornadas):
    mins = [hora_para_minutos(h) for h in horarios_str]
    equipe = [0] * len(mins)

    for j in jornadas:
        e = j["e"]

        if j["tipo"] == "completa":
            si, ri, sf = j["si"], j["ri"], j["sf"]
            if sf < e:
                sf += 1440
                if si < e: si += 1440
                if ri < e: ri += 1440

            for i, t in enumerate(mins):
                t24 = t + 1440 if t < e else t
                if (e <= t24 < si) or (ri <= t24 <= sf):
                    equipe[i] += j["qtd"]

        else:
            sf = j["sf"]
            if sf < e: sf += 1440
            for i, t in enumerate(mins):
                t24 = t + 1440 if t < e else t
                if e <= t24 <= sf:
                    equipe[i] += j["qtd"]

    return equipe


# =============== PROCESSAMENTO ===============

horarios = todos_horarios()

chegadas = {}
for linha in st.session_state.chegada.strip().split("\n"):
    p = linha.split()
    try:
        ton = float(p[1].replace(",", "."))
        chegadas[p[0]] = chegadas.get(p[0], 0) + ton
    except:
        pass

saidas = {}
for linha in st.session_state.saida.strip().split("\n"):
    p = linha.split()
    try:
        ton = float(p[1].replace(",", "."))
        saidas[p[0]] = saidas.get(p[0], 0) + ton
    except:
        pass

jornadas = parse_jornadas(st.session_state.conferente) + parse_jornadas(st.session_state.auxiliar)
equipe_total = calcular_equipe(horarios, jornadas)

df = pd.DataFrame({
    "Horário": horarios,
    "Chegada": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída":   [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe": equipe_total
})

max_ton = max(df["Chegada"].max(), df["Saída"].max(), 1) + 10
scale = max_ton / (df["Equipe"].max() + 10) if df["Equipe"].max() else 1
df["EquipeEscalada"] = df["Equipe"] * scale


# ===============================================================
#                       GRÁFICO (VISUAL AJUSTADO FINAL)
# ===============================================================

fig = go.Figure()

# Cores suaves
cor_verde = "#90EE90"
cor_vermelho = "#E74C3C"
cor_roxo = "#9B59B6"

# ---------- BARRAS ----------
fig.add_trace(go.Bar(
    x=df["Horário"],
    y=df["Chegada"],
    name="Chegada",
    marker_color=cor_verde,
    hovertemplate="%{y} Ton<extra></extra>",
))

fig.add_trace(go.Bar(
    x=df["Horário"],
    y=df["Saída"],
    name="Saída",
    marker_color=cor_vermelho,
    hovertemplate="%{y} Ton<extra></extra>",
))

# ---------- LINHA DA EQUIPE ----------
fig.add_trace(go.Scatter(
    x=df["Horário"],
    y=df["EquipeEscalada"],
    mode="lines+markers",
    name="Equipe",
    line=dict(color=cor_roxo, width=3),
    marker=dict(size=7, color=cor_roxo),
    hovertemplate="Equipe: %{customdata}<extra></extra>",
    customdata=df["Equipe"]
))

# ===============================================================
#                ANOTAÇÕES (RÓTULOS COLORIDOS)
# ===============================================================

anotacoes = []

# Rótulos de Chegada
for x, y in zip(df["Horário"], df["Chegada"]):
    if y > 0:
        anotacoes.append(dict(
            x=x, y=y,
            text=f"+{y}",
            showarrow=False,
            yshift=15,
            font=dict(color=cor_verde, size=14),
            bordercolor=cor_verde,
            borderwidth=1,
            bgcolor="white",
            opacity=1
        ))

# Rótulos de Saída
for x, y in zip(df["Horário"], df["Saída"]):
    if y > 0:
        anotacoes.append(dict(
            x=x, y=y,
            text=f"-{y}",
            showarrow=False,
            yshift=15,
            font=dict(color=cor_vermelho, size=14),
            bordercolor=cor_vermelho,
            borderwidth=1,
            bgcolor="white",
            opacity=1
        ))

# Rótulos da Equipe
for x, y_real, y_scaled in zip(df["Horário"], df["Equipe"], df["EquipeEscalada"]):
    if y_real > 0:
        anotacoes.append(dict(
            x=x, y=y_scaled,
            text=str(y_real),
            showarrow=False,
            yshift=15,
            font=dict(color=cor_roxo, size=14),
            bordercolor=cor_roxo,
            borderwidth=1,
            bgcolor="white",
            opacity=1,
        ))

fig.update_layout(annotations=anotacoes)

# ---------- LAYOUT ----------
fig.update_layout(
    title="Produção × Equipe – Chegada / Saída / Equipe",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escala)",
    height=820,
    barmode="stack",
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white",
    bargap=0.15,
    margin=dict(l=70, r=70, t=110, b=160),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5
    ),
)

st.plotly_chart(fig, use_container_width=True)

# ===============================================================
#                       DOWNLOAD EXCEL
# ===============================================================

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Dados")
buffer.seek(0)

st.download_button(
    "Baixar Excel Completo",
    buffer,
    "producao_cd_final.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ===============================================================
#                     CAMPOS DE EDIÇÃO
# ===============================================================

st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.session_state.chegada = st.text_area("Chegadas (hora ton)", st.session_state.chegada, height=300)
    st.session_state.conferente = st.text_area("Jornadas Conferentes", st.session_state.conferente, height=300)

with c2:
    st.session_state.saida = st.text_area("Saídas (hora ton)", st.session_state.saida, height=300)
    st.session_state.auxiliar = st.text_area("Jornadas Auxiliares", st.session_state.auxiliar, height=300)

