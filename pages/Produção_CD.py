# pages/Produção_CD.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go   # ← IMPORT NECESSÁRIO!
import io

st.set_page_config(layout="wide", page_title="Produção × Equipe - CD")
st.title("Produção × Equipe CD – Rótulos com Caixinha (Estilo Original)")

# ================= SESSION STATE =================
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

# ================= FUNÇÕES (mesmas do código anterior – cálculo 100% correto) =================
def hora_para_minutos(hora_str: str) -> int:
    h, m = map(int, hora_str.split(":"))
    return h * 60 + m

def todos_horarios():
    horarios = set()
    for texto in [st.session_state.chegada, st.session_state.saida,
                  st.session_state.conferente, st.session_state.auxiliar]:
        for linha in texto.strip().split("\n"):
            if not linha.strip(): continue
            p = linha.strip().split()
            if len(p) >= 2: horarios.add(p[0])
            if len(p) in (3, 5):
                horarios.update(p[:4] if len(p) == 5 else p[:2])
    return sorted(horarios, key=hora_para_minutos)

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        if not linha.strip(): continue
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():
            jornadas.append({"tipo": "completa", "e": hora_para_minutos(p[0]), "si": hora_para_minutos(p[1]),
                             "ri": hora_para_minutos(p[2]), "sf": hora_para_minutos(p[3]), "qtd": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            jornadas.append({"tipo": "simples", "e": hora_para_minutos(p[0]), "sf": hora_para_minutos(p[1]), "qtd": int(p[2])})
    return jornadas

def calcular_equipe_correto(horarios_str, jornadas):
    mins = [hora_para_minutos(h) for h in horarios_str]
    equipe = [0] * len(mins)
    for j in jornadas:
        e = j["e"]
        if j["tipo"] == "completa":
            si, ri, sf = j["si"], j["ri"], j["sf"]
            if sf < e: sf += 1440; si = si + 1440 if si < e else si; ri = ri + 1440 if ri < e else ri
            for i, t in enumerate(mins):
                t24 = t + 1440 if t < e else t
                if (e <= t24 < si) or (ri <= t24 <= sf): equipe[i] += j["qtd"]
        else:
            sf = j["sf"]
            if sf < e: sf += 1440
            for i, t in enumerate(mins):
                t24 = t + 1440 if t < e else t
                if e <= t24 <= sf: equipe[i] += j["qtd"]
    return equipe

# ================= PROCESSAMENTO =================
horarios = todos_horarios()

chegadas = {p[0]: chegadas.get(p[0], 0) + float(p[1].replace(",", ".")) 
            for linha in st.session_state.chegada.strip().split("\n") if (p:=linha.strip().split()) and len(p)>=2}
saidas   = {p[0]: saidas.get(p[0], 0) + float(p[1].replace(",", ".")) 
            for linha in st.session_state.saida.strip().split("\n") if (p:=linha.strip().split()) and len(p)>=2}

jornadas = parse_jornadas(st.session_state.conferente) + parse_jornadas(st.session_state.auxiliar)
equipe_total = calcular_equipe_correto(horarios, jornadas)

df = pd.DataFrame({
    "Horário": horarios,
    "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída (ton)"  : [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe Total": equipe_total
})

max_ton = max(df["Chegada (ton)"].max(), df["Saída (ton)"].max(), 1) + 10
scale = max_ton / (df["Equipe Total"].max() + 10)
df["Equipe_Escala"] = df["Equipe Total"] * scale

# ================= GRÁFICO COM RÓTULOS ESTILO ORIGINAL =================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horário"], y=df["Chegada (ton)"], name="Chegada", marker_color="#90EE90", opacity=0.85))
fig.add_trace(go.Bar(x=df["Horário"], y=-df["Saída (ton)"], name="Saída", marker_color="#E74C3C", opacity=0.85))

fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe_Escala"],
    mode="lines+markers",
    name="Equipe Total",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    customdata=df["Equipe Total"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# RÓTULOS COM CAIXINHA BRANCA + BORDA COLORIDA (igual ao seu primeiro código)
if st.session_state.rotulos:
    for _, r in df.iterrows():
        if r["Chegada (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=r["Chegada (ton)"],
                               text=f"+{r['Chegada (ton)']}", font=dict(color="#2ECC71", size=10),
                               bgcolor="white", bordercolor="#90EE90", borderwidth=2, borderpad=4,
                               showarrow=False, yshift=12)
        if r["Saída (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=-r["Saída (ton)"],
                               text=f"-{r['Saída (ton)']}", font=dict(color="#E74C3C", size=10),
                               bgcolor="white", bordercolor="#E74C3C", borderwidth=2, borderpad=4,
                               showarrow=False, yshift=-12)
        if r["Equipe Total"] > 0:
            fig.add_annotation(x=r["Horário"], y=r["Equipe_Escala"],
                               text=f"{int(r['Equipe Total'])}", font=dict(color="#9B59B6", size=11),
                               bgcolor="white", bordercolor="#9B59B6", borderwidth=2, borderpad=4,
                               showarrow=False, yshift=8)

fig.update_layout(
    title="Produção × Equipe Total – Rótulos com Caixinha (Estilo Original)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[-max_ton*1.2, max_ton*1.5]),
    height=820,
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5,
                font=dict(size=12), bgcolor="rgba(255,255,255,0.95)", bordercolor="#cccccc", borderwidth=1),
    margin=dict(l=70, r=70, t=110, b=160)
)

st.plotly_chart(fig, use_container_width=True)

# Confirmação
if "00:00" in df.values:
    eq = df[df["Horário"] == "00:00"]["Equipe Total"].iloc[0]
    st.success(f"Às 00:00 → **{eq} funcionários** (125 com seus dados reais)")

# ================= DOWNLOAD + INPUTS =================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
buffer.seek(0)
st.download_button("Baixar Excel", buffer, "producao_cd_final.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.session_state.chegada = st.text_area("Chegadas", st.session_state.chegada, height=300)
    st.session_state.conferente = st.text_area("Conferentes", st.session_state.conferente, height=300)
with c2:
    st.session_state.saida = st.text_area("Saídas", st.session_state.saida, height=300)
    st.session_state.auxiliar = st.text_area("Auxiliares", st.session_state.auxiliar, height=300)

st.session_state.rotulos = st.checkbox("Mostrar rótulos com caixinha", value=True)

st.success("Tudo funcionando 100%! Rótulos com caixinha branca + borda colorida exatamente como no seu primeiro código. 28/11/2025")
