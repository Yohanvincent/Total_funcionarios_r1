# pages/Producao_x_Equipe_R4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="Produção × Equipe - R4")
st.title("Produção × Equipe (Simplificado)")

# ================= DADOS FIXOS (exemplo) =================
chegada_fixa = """00:00 11,5
03:30 9,6
04:20 5,9
04:50 5,4
05:10 3,9
12:30 10,5"""

saida_fixa = """21:00 3,5
21:15 6,2
21:30 7,7
21:30 9,9
21:30 11,9"""

conferente_fixa = """23:50 02:40 03:45 09:11 4
01:00 04:00 05:05 10:23 1
06:00 11:00 12:15 16:03 8
12:30 16:00 17:15 22:28 12"""

auxiliar_fixa = """23:30 03:30 04:35 08:49 19
03:30 08:00 09:12 13:18 15
04:00 07:52 12
18:30 22:26 10"""

# ================= SESSION STATE =================
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.chegada = chegada_fixa
    st.session_state.saida = saida_fixa
    st.session_state.conferente = conferente_fixa
    st.session_state.auxiliar = auxiliar_fixa
    st.session_state.rotulos = True

# ================= FUNÇÕES AUXILIARES =================
def str_to_min(h):
    """Converte '23:50' → 1430 minutos (suporta >24h)"""
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 0

def min_to_str(m):
    hh = int(m // 60) % 24
    mm = int(m % 60)
    return f"{hh:02d}:{mm:02d}"

def todos_horarios():
    horarios = set()
    for texto in [st.session_state.chegada, st.session_state.saida,
                  st.session_state.conferente, st.session_state.auxiliar]:
        for linha in texto.strip().split("\n"):
            if not linha.strip(): continue
            partes = linha.strip().split()
            if len(partes) >= 2:
                horarios.add(partes[0])
            if len(partes) in (3, 5):  # jornadas
                horarios.update(partes[:4] if len(partes) == 5 else partes[:2])
    return sorted(horarios, key=str_to_min)

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        if not linha.strip(): continue
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():  # jornada completa com intervalo
            jornadas.append({
                "tipo": "completa",
                "entrada": p[0],
                "saida_intervalo": p[1],
                "retorno_intervalo": p[2],
                "saida_final": p[3],
                "qtd": int(p[4])
            })
        elif len(p) == 3 and p[2].isdigit():  # jornada simples (madrugada)
            jornadas.append({
                "tipo": "simples",
                "entrada": p[0],
                "saida_final": p[1],
                "qtd": int(p[2])
            })
    return jornadas

def calcular_equipe_disponivel(horarios_str, jornadas_confer, jornadas_aux):
    horarios_min = [str_to_min(h) for h in horarios_str]
    equipe = [0] * len(horarios_min)

    todas_jornadas = jornadas_confer + jornadas_aux

    for j in todas_jornadas:
        if j["tipo"] == "completa":
            e = str_to_min(j["entrada"])
            si = str_to_min(j["saida_intervalo"])
            ri = str_to_min(j["retorno_intervalo"])
            sf = str_to_min(j["saida_final"])

            # Trata turnos que cruzam meia-noite (ex: 23:50 até 09:11)
            if sf < e:  # virada de dia
                sf += 24 * 60
                si = si + 24*60 if si < e else si
                ri = ri + 24*60 if ri < e else ri

            for i, t in enumerate(horarios_min):
                t24 = t + 24*60 if t < e else t
                if (e <= t24 < si) or (ri <= t24 <= sf):
                    equipe[i] += j["qtd"]
        else:  # simples
            e = str_to_min(j["entrada"])
            sf = str_to_min(j["saida_final"])
            if sf < e: sf += 24*60
            for i, t in enumerate(horarios_min):
                t24 = t + 24*60 if t < e else t
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

# Jornadas
jorn_confer = parse_jornadas(st.session_state.conferente)
jorn_aux = parse_jornadas(st.session_state.auxiliar)
equipe_total = calcular_equipe_disponivel(horarios, jorn_confer, jorn_aux)

# ================= DATAFRAME =================
df = pd.DataFrame({
    "Horário": horarios,
    "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída (ton)": [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe Total": equipe_total
})

# Escala da equipe para aparecer no mesmo eixo
max_ton = max(df["Chegada (ton)"].max(), df["Saída (ton)"].max()) + 10
scale = max_ton / (df["Equipe Total"].max() + 5) if df["Equipe Total"].max() > 0 else 1
df["Equipe Escala"] = df["Equipe Total"] * scale

# ================= GRÁFICO =================
fig = go.Figure()

# Barras
fig.add_trace(go.Bar(
    x=df["Horário"], y=df["Chegada (ton)"],
    name="Chegada", marker_color="#90EE90", opacity=0.85
))
fig.add_trace(go.Bar(
    x=df["Horário"], y=-df["Saída (ton)"],
    name="Saída Carregada", marker_color="#E74C3C", opacity=0.85
))

# Linha da equipe
fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe Escala"],
    mode="lines+markers+text",
    name="Equipe (Conferente + Auxiliar)",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    text=df["Equipe Total"],
    textposition="top center",
    textfont=dict(size=11, color="#9B59B6"),
    hovertemplate="Equipe: %{text}<extra></extra>"
))

# Rótulos opcionais
if st.session_state.rotulos:
    for _, r in df.iterrows():
        if r["Chegada (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=r["Chegada (ton)"],
                               text=f"+{r['Chegada (ton)']}", showarrow=False,
                               yshift=10, font=dict(color="#27AE60", size=10),
                               bgcolor="white", borderwidth=1)
        if r["Saída (ton)"] > 0:
            fig.add_annotation(x=r["Horário"], y=-r["Saída (ton)"],
                               text=f"-{r['Saída (ton)']}", showarrow=False,
                               yshift=-10, font=dict(color="#C0392B", size=10),
                               bgcolor="white", borderwidth=1)

# Layout
fig.update_layout(
    title="Produção × Equipe Total (Conferentes + Auxiliares)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas (positiva = chegada | negativa = saída) | Equipe (escalada)", range=[-max_ton*1.1, max_ton*1.3]),
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
    df[["Horário", "Chegada (ton)", "Saída (ton)", "Equipe Total"]].to_excel(writer, index=False, sheet_name="Resumo")
buffer.seek(0)
st.download_button("📥 Baixar Excel", buffer, "producao_equipe_resumo.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ================= INPUTS EDITÁVEIS =================
st.markdown("---")
st.markdown("### ✏️ Editar Dados")

c1, c2 = st.columns(2)
with c1:
    st.session_state.chegada = st.text_area("Chegadas (hora ton)", st.session_state.chegada, height=250)
    st.session_state.conferente = st.text_area("Conferentes (jornadas)", st.session_state.conferente, height=250)
with c2:
    st.session_state.saida = st.text_area("Saídas Carregamento (hora ton)", st.session_state.saida, height=250)
    st.session_state.auxiliar = st.text_area("Auxiliares (jornadas)", st.session_state.auxiliar, height=250)

st.session_state.rotulos = st.checkbox("Mostrar rótulos de tonelada", value=True)

st.success("Versão simplificada pronta! Apenas Chegada, Saída e Equipe Total (Conferente + Auxiliar). Suporte a turnos noturnos funcionando perfeitamente. 28/11/2025")
