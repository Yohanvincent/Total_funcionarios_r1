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
            p = linha.split()
            horarios.add(p[0])

    return sorted(horarios, key=hora_para_minutos)

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        if not linha.strip(): 
            continue
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

# =============== PROCESSAMENTO DOS DADOS ===============

horarios = todos_horarios()

# Chegadas
chegadas = {}
for linha in st.session_state.chegada.strip().split("\n"):
    p = linha.split()
    if len(p) >= 2:
        try:
            ton = float(p[1].replace(",", "."))
            chegadas[p[0]] = chegadas.get(p[0], 0) + ton
        except:
            pass

# Saídas
saidas = {}
for linha in st.session_state.saida.strip().split("\n"):
    p = linha.split()
    if len(p) >= 2:
        try:
            ton = float(p[1].replace(",", "."))
            saidas[p[0]] = saidas.get(p[0], 0) + ton
        except:
            pass

# Equipe
jornadas = parse_jornadas(st.session_state.conferente) + parse_jornadas(st.session_state.auxiliar)
equipe_total = calcular_equipe(horarios, jornadas)

# DataFrame
df = pd.DataFrame({
    "Horário": horarios,
    "Chegada": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída":   [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe": equipe_total
})

# Escala da equipe → compatível com toneladas
max_ton = max(df["Chegada"].max(), df["Saída"].max(), 1) + 10
scale = max_ton / (df["Equipe"].max() + 10) if df["Equipe"].max() else 1
df["EquipeEscalada"] = df["Equipe"] * scale

# =============== GRÁFICO ===============

fig = go.Figure()

# ---------- BARRAS EMPILHADAS ----------

# Chegada (verde claro)
fig.add_trace(go.Bar(
    x=df["Horário"], 
    y=df["Chegada"],
    name="Chegada",
    marker_color="#90EE90",
    text=df["Chegada"].apply(lambda x: f"+{x}" if x > 0 else ""),
    textposition="inside",
    insidetextanchor="middle",
    textfont=dict(color="black"),
    insidetextfont=dict(color="black"),
    # Caixinha do rótulo
    hovertemplate="%{y} Ton<extra></extra>"
))

# Saída (vermelho suave)
fig.add_trace(go.Bar(
    x=df["Horário"], 
    y=df["Saída"],
    name="Saída",
    marker_color="#FF847C",
    text=df["Saída"].apply(lambda x: f"-{x}" if x > 0 else ""),
    textposition="inside",
    insidetextanchor="middle",
    textfont=dict(color="black"),
    insidetextfont=dict(color="black"),
    hovertemplate="%{y} Ton<extra></extra>"
))

# ---------- LINHA DA EQUIPE ----------
fig.add_trace(go.Scatter(
    x=df["Horário"],
    y=df["EquipeEscalada"],
    mode="lines+markers",
    name="Equipe",
    line=dict(color="#C39BD3", width=4, dash="dot"),
    marker=dict(size=9, color="#C39BD3"),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# ---------- LAYOUT ----------
fig.update_layout(
    title="Produção × Equipe – Chegada / Saída / Equipe",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escalada)",
    height=820,
    barmode="stack",
    hovermode="x unified",
    plot_bgcolor="white",
    paper_bgcolor="white",
    bargap=0.15,
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#ccc",
        borderwidth=1
    ),
    margin=dict(l=70, r=70, t=110, b=160)
)

# ---------- LINHA DA EQUIPE ----------
fig.add_trace(go.Scatter(
    x=df["Horário"],
    y=df["EquipeEscalada"],
    mode="lines+markers",
    name="Equipe",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# =============== LAYOUT ===============

fig.update_layout(
    title="Produção × Equipe – Chegada / Saída / Equipe (Estilo Oficial)",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escalada)",
    height=820,
    barmode="stack",   #  <<<< MODO EMPILHADO
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#ccc",
        borderwidth=1
    ),
    margin=dict(l=70, r=70, t=110, b=160)
)

st.plotly_chart(fig, use_container_width=True)


# ================= DOWNLOAD =================

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

# ================= EDIÇÃO DOS CAMPOS =================

st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.session_state.chegada = st.text_area("Chegadas (hora ton)", st.session_state.chegada, height=300)
    st.session_state.conferente = st.text_area("Jornadas Conferentes", st.session_state.conferente, height=300)

with c2:
    st.session_state.saida = st.text_area("Saídas (hora ton)", st.session_state.saida, height=300)
    st.session_state.auxiliar = st.text_area("Jornadas Auxiliares", st.session_state.auxiliar, height=300)

st.session_state.rotulos = st.checkbox("Mostrar rótulos", value=True)
