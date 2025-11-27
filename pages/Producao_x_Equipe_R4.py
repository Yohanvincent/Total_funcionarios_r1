# pages/Producao_x_Equipe_R4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="Produção vs Equipe - R4")

# ==================== TÍTULO E GRÁFICO PRIMEIRO =================
st.title("Produção vs Equipe + Janelas Críticas com Toneladas (V4 Final)")

# ================= DADOS FIXOS =================
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

entrega_fixa = """07:40 3,0
08:00 7,0
08:10 9,0
08:20 10
08:20 12,2
09:00 15,2
14:00 8,6
14:00 7,5
14:00 7,0
14:20 3,0"""

coleta_fixa = """18:00 20,5
18:15 10,2
18:30 8
18:45 17,6
19:00 7,5
19:15 9,3
19:30 10"""

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

# ================= INICIALIZA SESSION STATE =================
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.nova_chegada = chegada_fixa
    st.session_state.nova_saida = saida_fixa
    st.session_state.entrega_input = entrega_fixa
    st.session_state.coleta_input = coleta_fixa
    st.session_state.nova_confer = confer_fixa
    st.session_state.nova_aux = aux_fixa
    st.session_state.rotulos = True

# ================= PROCESSAMENTO =================
chegada_txt   = st.session_state.nova_chegada
saida_txt     = st.session_state.nova_saida
entrega_input = st.session_state.entrega_input
coleta_input  = st.session_state.coleta_input
confer_txt    = st.session_state.nova_confer
aux_txt       = st.session_state.nova_aux
rotulos       = st.session_state.rotulos

# --- Processa Entrega e Coleta ---
entrega_dict = {}
for linha in entrega_input.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h = p[0]
        try: entrega_dict[h] = entrega_dict.get(h, 0) + float(p[1].replace(",", "."))
        except: pass

coleta_dict = {}
for linha in coleta_input.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h = p[0]
        try: coleta_dict[h] = coleta_dict.get(h, 0) + float(p[1].replace(",", "."))
        except: pass

# --- Extrai Chegada e Saída ---
def extrair_producao(texto):
    cheg, said = {}, {}
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
            if modo == "cheg": cheg[h] = cheg.get(h, 0) + v
            else: said[h] = said.get(h, 0) + v
        except: pass
    return cheg, said

cheg, said = extrair_producao(f"Cheg. Ton.\n{chegada_txt}\nSaida Ton.\n{saida_txt}")

# --- Jornadas e horários
def jornadas(t):
    j = []
    for l in t.strip().split("\n"):
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({"t":"c","e":p[0],"si":p[1],"ri":p[2],"sf":p[3],"q":int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"t":"m","e":p[0],"sf":p[1],"q":int(p[2])})
    return j

def min_hora(h):
    try: hh,mm = map(int,h.split(":")); return hh*60 + mm
    except: return 0

def todos_horarios(*texts):
    s = set()
    for t in texts:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) >= 2: s.add(p[0])
            if len(p) in (3,5): s.update(p[:-1])
    return sorted(s, key=min_hora)

jorn_conf = jornadas(confer_txt)
jorn_aux  = jornadas(aux_txt)
horarios = todos_horarios(chegada_txt, saida_txt, confer_txt, aux_txt, entrega_input, coleta_input)

def calcular_equipe(jlist, hrs):
    tl = [min_hora(h) for h in hrs]
    eq = [0]*len(tl)
    for j in jlist:
        e = min_hora(j["e"])
        if j["t"]=="c":
            si = min_hora(j["si"])
            ri = min_hora(j["ri"])
            sf = min_hora(j["sf"])
            for i,t in enumerate(tl):
                if (e<=t<si) or (ri<=t<=sf): eq[i] += j["q"]
        else:
            sf = min_hora(j["sf"])
            for i,t in enumerate(tl):
                if e<=t<=sf: eq[i] += j["q"]
    return eq

eq_total = [a+b for a,b in zip(calcular_equipe(jorn_conf,horarios), calcular_equipe(jorn_aux,horarios))]

# DataFrame
df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": [round(cheg.get(h,0),1) for h in horarios],
    "Saida_Ton" : [round(said.get(h,0),1) for h in horarios],
    "Entrega_Ton": [round(entrega_dict.get(h,0),1) for h in horarios],
    "Coleta_Ton" : [round(coleta_dict.get(h,0),1) for h in horarios],
    "Equipe" : eq_total
})

max_ton = df[["Chegada_Ton","Saida_Ton","Entrega_Ton","Coleta_Ton"]].max().max() + 10
scale = max_ton / (df["Equipe"].max() + 5) if df["Equipe"].max() > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# ================= GRÁFICO LIMPO – SEM TRIÂNGULOS! =================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada", marker_color="#90EE90", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Carregada", marker_color="#E74C3C", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Entrega_Ton"], name="Saída para Entrega", marker_color="#3498DB", opacity=0.9))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Coleta_Ton"], name="Retorno de Coleta", marker_color="#E67E22", opacity=0.9))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe Disponível",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    text=df["Equipe"],
    textposition="top center",
    textfont=dict(size=11, color="#9B59B6"),
    hovertemplate="Equipe: <b>%{text}</b> pessoas<extra></extra>"
))

# RÓTULOS (mantidos)
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"+{r['Chegada_Ton']}",
                               font=dict(color="#2ECC71", size=10, weight="bold"), showarrow=False, yshift=12)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"-{r['Saida_Ton']}",
                               font=dict(color="#E74C3C", size=10, weight="bold"), showarrow=False, yshift=12)
        if r["Entrega_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Entrega_Ton"], text=f"{r['Entrega_Ton']}",
                               font=dict(color="#2980B9", size=10, weight="bold"), showarrow=False, yshift=12)
        if r["Coleta_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Coleta_Ton"], text=f"{r['Coleta_Ton']}",
                               font=dict(color="#D35400", size=10, weight="bold"), showarrow=False, yshift=12)

fig.update_layout(
    title="",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.25]),
    height=800,
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=50, r=50, t=60, b=80)
)

st.plotly_chart(fig, use_container_width=True)

# Download Excel
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Operação Completa', index=False)
buffer.seek(0)
st.download_button("Baixar dados em Excel", buffer, f"operacao_{pd.Timestamp('today').strftime('%d%m%Y')}.xlsx")

# ================= INPUTS LÁ EMBAIXO =================
st.markdown("---")
st.markdown("### ✏️ Editar Dados (Opcional)")

c1, c2, c3 = st.columns(3)

with c1:
    st.session_state.nova_chegada = st.text_area("Chegadas", value=chegada_fixa, height=300, key="ch")
    st.session_state.nova_confer = st.text_area("Conferentes", value=confer_fixa, height=300, key="cf")

with c2:
    st.session_state.nova_saida = st.text_area("Saídas Carregamento", value=saida_fixa, height=300, key="sd")
    st.session_state.nova_aux = st.text_area("Auxiliares", value=aux_fixa, height=300, key="au")

with c3:
    st.markdown("#### Saída para Entrega")
    st.session_state.entrega_input = st.text_area("", value=entrega_fixa, height=150, key="ent")
    st.markdown("#### Retorno de Coleta")
    st.session_state.coleta_input = st.text_area("", value=coleta_fixa, height=150, key="col")
    st.session_state.rotulos = st.checkbox("Mostrar rótulos de tonelada", value=True)

st.success("Triângulos removidos com sucesso! Gráfico limpo e profissional ✓")
