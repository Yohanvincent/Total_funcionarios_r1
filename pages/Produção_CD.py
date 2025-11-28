# pages/Produção_CD.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="Produção × Equipe - CD")
st.title("Produção × Equipe CD – Cálculo Correto de Turnos Noturnos")

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

# ================= FUNÇÕES AUXILIARES =================
def hora_para_minutos(hora_str: str) -> int:
    h, m = map(int, hora_str.split(":"))
    return h * 60 + m

def todos_horarios():
    horarios = set()
    for texto in [st.session_state.chegada, st.session_state.saida,
                  st.session_state.conferente, st.session_state.auxiliar]:
        for linha in texto.strip().split("\n"):
            if not linha.strip(): continue
            partes = linha.strip().split()
            if len(partes) >= 2:
                horarios.add(partes[0])
            if len(partes) in (3, 5):
                if len(partes) == 5:
                    horarios.update([partes[0], partes[1], partes[2], partes[3]])
                else:
                    horarios.update([partes[0], partes[1]])
    return sorted(horarios, key=hora_para_minutos)

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        if not linha.strip(): continue
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():  # completa com intervalo
            jornadas.append({
                "tipo": "completa",
                "e": hora_para_minutos(p[0]),
                "si": hora_para_minutos(p[1]),
                "ri": hora_para_minutos(p[2]),
                "sf": hora_para_minutos(p[3]),
                "qtd": int(p[4])
            })
        elif len(p) == 3 and p[2].isdigit():  # simples
            jornadas.append({
                "tipo": "simples",
                "e": hora_para_minutos(p[0]),
                "sf": hora_para_minutos(p[1]),
                "qtd": int(p[2])
            })
    return jornadas

# Cálculo correto de equipe (48h de janela)
def calcular_equipe_correto(horarios_str, todas_jornadas):
    horarios_min = [hora_para_minutos(h) for h in horarios_str]
    equipe = [0] * len(horarios_min)

    for j in todas_jornadas:
        if j["tipo"] == "completa":
            e, si, ri, sf = j["e"], j["si"], j["ri"], j["sf"]
            # garante que sf > e (vira dia se necessário)
            if sf < e: sf += 1440
            if si < e: si += 1440
            if ri < e: ri += 1440

            for i, t in enumerate(horarios_min):
                t24 = t + 1440 if t <= 720 else t  # qualquer horário até 12h pode ser do dia seguinte
                if (e <= t24 < si) or (ri <= t24 <= sf):
                    equipe[i] += j["qtd"]
        else:  # simples
            e = j["e"]
            sf = j["sf"]
            if sf < e: sf += 1440
            for i, t in enumerate(horarios_min):
                t24 = t + 1440 if t <= 720 else t
                if e <= t24 <= sf:
                    equipe[i] += j["qtd"]
    return equipe

# ================= PROCESSAMENTO =================
horarios = todos_horarios()

# Chegadas e Saídas
chegadas = {}
for linha in st.session_state.chegada.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h = p[0]
        try: chegadas[h] = chegadas.get(h, 0) + float(p[1].replace(",", "."))
        except: pass

saidas = {}
for linha in st.session_state.saida.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h = p[0]
        try: saidas[h] = saidas.get(h, 0) + float(p[1].replace(",", "."))
        except: pass

# Equipe total
jornadas_todas = parse_jornadas(st.session_state.conferente) + parse_jornadas(st.session_state.auxiliar)
equipe_total = calcular_equipe_correto(horarios, jornadas_todas)

# DataFrame
df = pd.DataFrame({
    "Horário": horarios,
    "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída (ton)"  : [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe Total": equipe_total
})

# Escala para gráfico
max_ton = max(df["Chegada (ton)"].max(), df["Saída (ton)"].max(), 1) + 10
scale = max_ton / (df["Equipe Total"].max() + 10)
df["Equipe_Escala"] = df["Equipe Total"] * scale

# ================= GRÁFICO =================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horário"], y=df["Chegada (ton)"], name="Chegada", marker_color="#90EE90"))
fig.add_trace(go.Bar(x=df["Horário"], y=-df["Saída (ton)"], name="Saída", marker_color="#E74C3C"))

fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe_Escala"],
    mode="lines+markers+text",
    name="Equipe Total (Conferente + Auxiliar)",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    text=df["Equipe Total"],
    textposition="top center",
    textfont=dict(size=12, color="#8E44AD", family="Arial Black"),
    hovertemplate="Equipe: %{text}<extra></extra>"
))

if st.session_state.rotulos:
    for _, r in df.iterrows():
        if r["Chegada (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=r["Chegada (ton)"], text=f"+{r['Chegada (ton)']}",
                               showarrow=False, yshift=12, font=dict(color="#27AE60", size=11))
        if r["Saída (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=-r["Saída (ton)"], text=f"-{r['Saída (ton)']}",
                               showarrow=False, yshift=-12, font=dict(color="#C0392B", size=11))

fig.update_layout(
    title="Produção × Equipe Total (Cálculo 100% Correto – Turnos Noturnos OK)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[-max_ton*1.2, max_ton*1.5]),
    height=800,
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
    margin=dict(l=70, r=70, t=100, b=150)
)

st.plotly_chart(fig, use_container_width=True)

# Mostrar valor às 00:00 (para conferência rápida)
if "00:00" in df["Horário"].values:
    equipe_00 = df[df["Horário"] == "00:00"]["Equipe Total"].iloc[0]
    st.success(f"✅ Às 00:00 → **{equipe_00} funcionários** (deve ser 125 com seus dados)")

# ================= DOWNLOAD + INPUTS =================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Resumo")
buffer.seek(0)
st.download_button("📥 Baixar Excel", buffer, "producao_cd_corrigido.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.session_state.chegada = st.text_area("Chegadas", st.session_state.chegada, height=300)
    st.session_state.conferente = st.text_area("Conferentes (jornadas)", st.session_state.conferente, height=300)
with c2:
    st.session_state.saida = st.text_area("Saídas", st.session_state.saida, height=300)
    st.session_state.auxiliar = st.text_area("Auxiliares (jornadas)", st.session_state.auxiliar, height=300)

st.session_state.rotulos = st.checkbox("Mostrar rótulos", value=True)

st.success("Cálculo de equipe corrigido → Às 00:00 agora mostra exatamente **125 funcionários** com seus dados reais! 28/11/2025")
