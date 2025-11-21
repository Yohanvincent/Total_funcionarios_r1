# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("🚛 Produção vs Equipe + Horários Críticos (Pontos no Gráfico)")

rotulos = st.checkbox("Mostrar rótulos de valores", value=True)
mostrar_pontos = st.checkbox("Mostrar pontos de Saída Entrega e Retorno Coleta", value=True)

# ==============================================================
# 1 – ENTRADA DE DADOS
# ==============================================================
st.markdown("### ✏️ Cole seus dados (ou use os padrões)")

col1, col2, col3 = st.columns([2, 2, 1.8])

with col1:
    nova_chegada = st.text_area("Chegadas (horário tonelada)", height=220)
    nova_confer = st.text_area("Conferentes (entrada saída_int retorno_int saída_final qtd)", height=220)

with col2:
    nova_saida = st.text_area("Saídas carregadas (horário tonelada)", height=220)
    nova_aux = st.text_area("Auxiliares (entrada saída_final qtd)", height=220)

with col3:
    st.markdown("#### Horários Críticos (um por linha)")
    janelas = st.text_area(
        "Formato: horário descrição",
        height=380,
        value="""18:00 Retorno de Coleta
18:15 Retorno de Coleta
18:30 Retorno de Coleta
18:45 Retorno de Coleta
19:00 Retorno de Coleta
19:15 Retorno de Coleta
19:30 Retorno de Coleta
07:40 Saída Para Entrega
08:00 Saída Para Entrega
08:10 Saída Para Entrega
08:20 Saída Para Entrega
09:00 Saída Para Entrega
14:00 Saída Para Entrega
14:20 Saída Para Entrega"""
    )

# ==============================================================
#  # 2 – DADOS PADRÃO
# ==============================================================
chegada_fixa = """03:30 9,6
04:20 5,9
04:50 5,4
04:50 4,4
05:10 3,9
05:15 1,8
05:30 4,5
05:45 6,3
05:45 8,9
05:50 3,7
06:20 3,1
07:10 0,9
09:15 1,0
11:00 0,8
12:30 10,5"""

saida_fixa = """21:00 3,5
21:15 6,2
21:15 2,3
21:30 7,7
21:30 9,9
21:30 2,8
21:30 9,7
21:30 9,4
21:30 11,9"""

confer_fixa = """03:30 08:00 09:12 13:18 15
06:00 11:00 12:15 16:03 1
07:00 12:00 13:12 17:00 1
07:55 11:15 12:30 17:58 1
08:00 12:00 14:00 18:48 1
12:30 16:00 17:15 22:28 13"""

aux_fixa = """03:30 07:18 3
03:30 08:00 09:12 13:18 19
04:00 07:52 12
07:55 11:15 12:30 17:58 1
12:30 16:00 17:15 22:28 5
18:30 22:26 18"""

# ==============================================================
# 3 – APLICA DADOS
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_fixa
saida_txt   = nova_saida.strip()   if nova_saida.strip()   else saida_fixa
confer_txt  = nova_confer.strip()  if nova_confer.strip()  else confer_fixa
aux_txt     = nova_aux.strip()     if nova_aux.strip()     else aux_fixa

# Processa horários críticos
saida_entrega = []
retorno_coleta = []
for linha in janelas.strip().split("\n"):
    if not linha.strip(): continue
    partes = linha.strip().split(maxsplit=1)
    hora = partes[0]
    desc = partes[1].lower() if len(partes) > 1 else ""
    if "saída" in desc or "entrega" in desc:
        saida_entrega.append(hora)
    elif "retorno" in desc or "coleta" in desc:
        retorno_coleta.append(hora)

# ==============================================================
# 4 – FUNÇÕES (100% funcionais)
# ==============================================================
def extrair_producao(texto):
    cheg = {}
    said = {}
    modo = None
    for l in texto.strip().split("\n"):
        l = l.strip()
        if l == "Cheg. Ton.": modo = "cheg"; continue
        if l == "Saida Ton.": modo = "said"; continue
        if not l or modo is None: continue
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

texto_producao = f"Cheg. Ton.\n{chegada_txt}\nSaida Ton.\n{saida_txt}"
cheg, said = extrair_producao(texto_producao)

def jornadas(t):
    j = []
    for l in t.strip().split("\n"):
        p = l.strip().split()
        if not p: continue
        if len(p) == 5 and p[4].isdigit():
            j.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"t": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return j

def min_hora(h):
    try: hh, mm = map(int, h.split(":")); return hh*60 + mm
    except: return 0

def get_horarios_from_texts(*texts):
    h = set()
    for t in texts:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3, 5):
                h.update(p[:-1])
    return sorted(h, key=min_hora)

jornadas_conf = jornadas(confer_txt)
jornadas_aux = jornadas(aux_txt)

todas_horas = set(cheg) | set(said) | set(saida_entrega) | set(retorno_coleta)
todas_horas.update(get_horarios_from_texts(confer_txt, aux_txt))
horarios = sorted(todas_horas, key=min_hora)

def calcular_equipe(jornadas_list, horarios):
    tl = [min_hora(h) for h in horarios]
    eq = [0] * len(tl)
    for j in jornadas_list:
        e = min_hora(j["e"])
        if j["t"] == "c":
            si = min_hora(j["si"])
            ri = min_hora(j["ri"])
            sf = min_hora(j["sf"])
            for i, t in enumerate(tl):
                if (e <= t < si) or (ri <= t <= sf):
                    eq[i] += j["q"]
        else:
            sf = min_hora(j["sf"])
            for i, t in enumerate(tl):
                if e <= t <= sf:
                    eq[i] += j["q"]
    return eq

eq_conf = calcular_equipe(jornadas_conf, horarios)
eq_aux = calcular_equipe(jornadas_aux, horarios)
eq_total = [c + a for c, a in zip(eq_conf, eq_aux)]

cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
said_val = [round(said.get(h, 0), 1) for h in horarios]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq_total
})

# Escala da equipe
max_ton = max(max(cheg_val or [0]), max(said_val or [0])) + 10
scale = max_ton / (max(eq_total or [0]) + 5)
df["Equipe_Escalada"] = df["Equipe"] * scale

# ==============================================================
# GRÁFICO COM PONTOS GRANDES NOS HORÁRIOS CRÍTICOS
# ==============================================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada (ton)", marker_color="#90EE90"))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Carregada (ton)", marker_color="#E74C3C"))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers+text",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    text=df["Equipe"],
    textposition="top center",
    hovertemplate="Equipe: %{text} pessoas"
))

# PONTOS GRANDES NOS HORÁRIOS CRÍTICOS
if mostrar_pontos:
    # Saída para Entrega → ponto azul grande
    df_entrega = df[df["Horario"].isin(saida_entrega)]
    fig.add_trace(go.Scatter(
        x=df_entrega["Horario"], y=[max_ton * 1.05] * len(df_entrega),
        mode="markers+text",
        marker=dict(color="#2980B9", size=16, symbol="triangle-down"),
        text=["Saída Entrega"] * len(df_entrega),
        textposition="top center",
        name="Saída Entrega",
        hoverinfo="text"
    ))

    # Retorno de Coleta → ponto laranja grande
    df_coleta = df[df["Horario"].isin(retorno_coleta)]
    fig.add_trace(go.Scatter(
        x=df_coleta["Horario"], y=[max_ton * 1.05] * len(df_coleta),
        mode="markers+text",
        marker=dict(color="#E67E22", size=16, symbol="triangle-up"),
        text=["Retorno Coleta"] * len(df_coleta),
        textposition="bottom center",
        name="Retorno Coleta",
        hoverinfo="text"
    ))

# Rótulos normais
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=str(r["Chegada_Ton"]), yshift=10, showarrow=False, font=dict(color="#27AE60"))
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=str(r["Saida_Ton"]), yshift=10, showarrow=False, font=dict(color="#C0392B"))

fig.update_layout(
    title="Capacidade Operacional – Pontos destacam Saídas e Retornos Críticos",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.15]),
    height=750,
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# DOWNLOAD
# ==============================================================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Produção", index=False)
    pd.DataFrame({"Saída para Entrega": saida_entrega, "Retorno de Coleta": retorno_coleta}).to_excel(writer, sheet_name="Horários Críticos", index=False)
buffer.seek(0)

st.download_button("📊 Baixar Relatório Completo", buffer, "capacidade_com_pontos.xlsx")

st.success("App rodando 100% – Pontos grandes nos horários críticos adicionados com sucesso! (21/11/2025)")
