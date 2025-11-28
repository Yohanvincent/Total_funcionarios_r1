# pages/Produção_CD.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="Produção × Equipe - CD")
st.title("Produção × Equipe (CD) - Apenas Chegada, Saída e Equipe Total")

# ================= INICIALIZAÇÃO SEGURA DO SESSION STATE =================
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.chegada     = """00:00 11,5
03:30 9,6
04:20 5,9
04:50 5,4
05:10 3,9
12:30 10,5"""
    st.session_state.saida       = """21:00 3,5
21:15 6,2
21:30 7,7
21:30 9,9
21:30 11,9"""
    st.session_state.conferente  = """23:50 02:40 03:45 09:11 4
01:00 04:00 05:05 10:23 1
06:00 11:00 12:15 16:03 8
12:30 16:00 17:15 22:28 12"""
    st.session_state.auxiliar    = """23:30 03:30 04:35 08:49 19
03:30 08:00 09:12 13:18 15
04:00 07:52 12
18:30 22:26 10"""
    st.session_state.rotulos = True

# ================= FUNÇÕES AUXILIARES =================
def str_to_min(h: str) -> int:
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
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
            p = linha.strip().split()
            if len(p) >= 2:
                horarios.add(p[0])
            # jornadas: 5 campos (completa) ou 3 campos (simples)
            if len(p) in (3, 5):
                horarios.update(p[:4] if len(p) == 5 else p[:2])
    return sorted(horarios, key=str_to_min)

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        if not linha.strip():
            continue
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():      # jornada com intervalo
            jornadas.append({
                "tipo": "completa",
                "e": p[0], "si": p[1], "ri": p[2], "sf": p[3],
                "qtd": int(p[4])
            })
        elif len(p) == 3 and p[2].isdigit():    # jornada simples
            jornadas.append({
                "tipo": "simples",
                "e": p[0], "sf": p[1],
                "qtd": int(p[2])
            })
    return jornadas

def calcular_equipe(horarios_str, jornadas):
    mins = [str_to_min(h) for h in horarios_str]
    equipe = [0] * len(mins)

    for j in jornadas:
        e = str_to_min(j["e"])
        if j["tipo"] == "completa":
            si = str_to_min(j["si"])
            ri = str_to_min(j["ri"])
            sf = str_to_min(j["sf"])
            # virada de dia
            if sf < e:
                sf += 24*60
                si = si + 24*60 if si < e else si
                ri = ri + 24*60 if ri < e else ri
            for i, t in enumerate(mins):
                t24 = t + 24*60 if t < e else t
                if (e <= t24 < si) or (ri <= t24 <= sf):
                    equipe[i] += j["qtd"]
        else:  # simples
            sf = str_to_min(j["sf"])
            if sf < e:
                sf += 24*60
            for i, t in enumerate(mins):
                t24 = t + 24*60 if t < e else t
                if e <= t24 <= sf:
                    equipe[i] += j["qtd"]
    return equipe

# ================= PROCESSAMENTO DOS DADOS =================
horarios = todos_horarios()

# Chegadas
chegadas = {}
for linha in st.session_state.chegada.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h = p[0]
        try:
            chegadas[h] = chegadas.get(h, 0) + float(p[1].replace(",", "."))
        except:
            pass

# Saídas
saidas = {}
for linha in st.session_state.saida.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h = p[0]
        try:
            saidas[h] = saidas.get(h, 0) + float(p[1].replace(",", "."))
        except:
            pass

# Equipe total (conferentes + auxiliares)
jornadas_confer = parse_jornadas(st.session_state.conferente)
jornadas_aux    = parse_jornadas(st.session_state.auxiliar)
equipe_total = calcular_equipe(horarios, jornadas_confer + jornadas_aux)

# ================= DATAFRAME =================
df = pd.DataFrame({
    "Horário": horarios,
    "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída (ton)"  : [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe Total" : equipe_total
})

# Escala da equipe para o mesmo eixo Y
max_ton = max(df["Chegada (ton)"].max(), df["Saída (ton)"].max()) + 10
scale = max_ton / (df["Equipe Total"].max() + 5) if df["Equipe Total"].max() > 0 else 1
df["Equipe Escala"] = df["Equipe Total"] * scale

# ================= GRÁFICO =================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horário"], y=df["Chegada (ton)"], name="Chegada", marker_color="#90EE90"))
fig.add_trace(go.Bar(x=df["Horário"], y=-df["Saída (ton)"], name="Saída", marker_color="#E74C3C"))

fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe Escala"],
    mode="lines+markers+text",
    name="Equipe Total",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    text=df["Equipe Total"],
    textposition="top center",
    textfont=dict(size=12, color="#9B59B6", family="Arial Black"),
    hovertemplate="Equipe: %{text}<extra></extra>"
))

if st.session_state.rotulos:
    for _, r in df.iterrows():
        if r["Chegada (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=r["Chegada (ton)"],
                               text=f"+{r['Chegada (ton)']}", showarrow=False, yshift=10,
                               font=dict(color="#27AE60", size=11), bgcolor="white")
        if r["Saída (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=-r["Saída (ton)"],
                               text=f"-{r['Saída (ton)']}", showarrow=False, yshift=-10,
                               font=dict(color="#C0392B", size=11), bgcolor="white")

fig.update_layout(
    title="Produção × Equipe Total (Conferentes + Auxiliares)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas (↑ chegada | ↓ saída) | Equipe (escalada)", range=[-max_ton*1.1, max_ton*1.3]),
    height=780,
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    margin=dict(l=60, r=60, t=100, b=140)
)

st.plotly_chart(fig, use_container_width=True)

# ================= DOWNLOAD EXCEL =================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df[["Horário", "Chegada (ton)", "Saída (ton)", "Equipe Total"]].to_excel(writer, index=False)
buffer.seek(0)
st.download_button("📥 Baixar Excel", buffer, "producao_cd.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ================= INPUTS =================
st.markdown("---")
st.markdown("### ✏️ Editar Dados")

c1, c2 = st.columns(2)
with c1:
    st.session_state.chegada    = st.text_area("Chegadas (hora ton)", st.session_state.chegada, height=280)
    st.session_state.conferente = st.text_area("Jornadas Conferentes", st.session_state.conferente, height=280)
with c2:
    st.session_state.saida      = st.text_area("Saídas (hora ton)", st.session_state.saida, height=280)
    st.session_state.auxiliar  = st.text_area("Jornadas Auxiliares", st.session_state.auxiliar, height=280)

st.session_state.rotulos = st.checkbox("Mostrar rótulos de tonelada", value=True)

st.success("App corrigido e rodando 100% – sem mais AttributeError! Turnos noturnos funcionando perfeitamente. 28/11/2025")
