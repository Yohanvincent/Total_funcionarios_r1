# pages/4_Producao_x_Equipe_V4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="Produção vs Equipe - V4 Final")

# ==================== TÍTULO E GRÁFICO PRIMEIRO ====================
st.title("Produção vs Equipe + Janelas Críticas com Toneladas (V4 Final)")

# ==================== DADOS FIXOS ATUALIZADOS (com seus novos valores reais) ====================
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

# <<< SEUS DADOS REAIS AGORA FIXOS E VISÍVEIS NOS CAMPOS >>>
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

# ==================== PROCESSAMENTO (com valores padrão já carregados) ====================
# Usa session_state para manter os valores ao editar
if "dados_prontos" not in st.session_state:
    st.session_state.dados_prontos = True
    st.session_state.nova_chegada = chegada_fixa
    st.session_state.nova_saida = saida_fixa
    st.session_state.entrega_input = entrega_fixa
    st.session_state.coleta_input = coleta_fixa
    st.session_state.nova_confer = confer_fixa
    st.session_state.nova_aux = aux_fixa
    st.session_state.rotulos = True
    st.session_state.mostrar_simbolos = True

# Captura valores atuais
chegada_txt = st.session_state.nova_chegada
saida_txt = st.session_state.nova_saida
entrega_input = st.session_state.entrega_input
coleta_input = st.session_state.coleta_input
confer_txt = st.session_state.nova_confer
aux_txt = st.session_state.nova_aux
rotulos = st.session_state.rotulos
mostrar_simbolos = st.session_state.mostrar_simbolos

# Processa Entrega e Coleta
entrega_dict = {}
for linha in entrega_input.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h, v = p[0], p[1].replace(",", ".")
        try: entrega_dict[h] = entrega_dict.get(h, 0) + float(v)
        except: pass

coleta_dict = {}
for linha in coleta_input.strip().split("\n"):
    if not linha.strip(): continue
    p = linha.strip().split()
    if len(p) >= 2:
        h, v = p[0], p[1].replace(",", ".")
        try: coleta_dict[h] = coleta_dict.get(h, 0) + float(v)
        except: pass

# Extrai chegadas e saídas
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

cheg, said = extrair_producao(f"Cheg. Ton.\n{chegada_txt}\nSaida Ton.\n{saida_txt}")

# Funções de jornada e horário
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
todas_horas = set(cheg) | set(said) | set(entrega_dict) | set(coleta_dict)
horas_equipe = get_horarios_from_texts(confer_txt, aux_txt)
todas_horas.update(horas_equipe)
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

eq_total = [a + b for a, b in zip(calcular_equipe(jornadas_conf, horarios), calcular_equipe(jornadas_aux, horarios))]

cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
said_val = [round(said.get(h, 0), 1) for h in horarios]
entrega_val = [round(entrega_dict.get(h, 0), 1) for h in horarios]
coleta_val = [round(coleta_dict.get(h, 0), 1) for h in horarios]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Entrega_Ton": entrega_val,
    "Coleta_Ton": coleta_val,
    "Equipe": eq_total
})

max_ton = max(max(cheg_val), max(said_val), max(entrega_val), max(coleta_val), 10) + 10
scale = max_ton / (max(eq_total) + 5)
df["Equipe_Escalada"] = df["Equipe"] * scale

# ==================== GRÁFICO (EXATAMENTE COMO VOCÊ QUERIA) ====================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada", marker_color="#90EE90", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Carregada", marker_color="#E74C3C", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Entrega_Ton"], name="Saída para Entrega", marker_color="#3498DB", opacity=0.9))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Coleta_Ton"], name="Retorno de Coleta", marker_color="#E67E67E22", opacity=0.9))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

if mostrar_simbolos:
    entrega_hrs = [h for h, t in entrega_dict.items() if t > 0]
    if entrega_hrs:
        fig.add_trace(go.Scatter(x=entrega_hrs, y=[max_ton * 1.08] * len(entrega_hrs),
                                 mode="markers", marker=dict(color="#2980B9", size=22, symbol="triangle-up"),
                                 name="Saída para Entrega", hoverinfo="skip"))
    coleta_hrs = [h for h, t in coleta_dict.items() if t > 0]
    if coleta_hrs:
        fig.add_trace(go.Scatter(x=coleta_hrs, y=[max_ton * 1.08] * len(coleta_hrs),
                                 mode="markers", marker=dict(color="#E67E22", size=22, symbol="triangle-down"),
                                 name="Retorno de Coleta", hoverinfo="skip"))

if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"+{r['Chegada_Ton']}",
                               font=dict(color="#2ECC71", size=9), bgcolor="white", bordercolor="#90EE90", borderwidth=1, showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"-{r['Saida_Ton']}",
                               font=dict(color="#E74C3C", size=9), bgcolor="white", bordercolor="#E74C3C", borderwidth=1, showarrow=False, yshift=10)
        if r["Entrega_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Entrega_Ton"], text=f"{r['Entrega_Ton']}",
                               font=dict(color="#2980B9", size=9), bgcolor="white", bordercolor="#3498DB", borderwidth=1, showarrow=False, yshift=10)
        if r["Coleta_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Coleta_Ton"], text=f"{r['Coleta_Ton']}",
                               font=dict(color="#D35400", size=9), bgcolor="white", bordercolor="#E67E22", borderwidth=1, showarrow=False, yshift=10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"],
                               text=f"{int(r['Equipe'])}",
                               font=dict(color="#9B59B6", size=9), bgcolor="white",
                               bordercolor="#9B59B6", borderwidth=1, showarrow=False, yshift=0, align="center")

fig.update_layout(
    title="Produção × Equipe × Saídas/Retornos com Toneladas (V4 Final)",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.2]),
    height=750,
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1, x=0),
    margin=dict(t=100)
)

st.plotly_chart(fig, use_container_width=True)

# Download
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Dados", index=False)
buffer.seek(0)
st.download_button("Baixar Excel Completo", buffer, "producao_v4_final.xlsx")

# ==================== SÓ AGORA: INPUTS LÁ EMBAIXO ====================
st.markdown("---")
st.markdown("### Cole novos dados (opcional – substitui os fixos)")

col_a, col_b, col_c = st.columns([2, 2, 2])

with col_a:
    nova_chegada = st.text_area("Chegadas (horário tonelada)", value=chegada_fixa, height=220, key="nova_chegada")
    nova_confer = st.text_area("Conferentes", value=confer_fixa, height=220, key="nova_confer")

with col_b:
    nova_saida = st.text_area("Saídas (horário tonelada)", value=saida_fixa, height=220, key="nova_saida")
    nova_aux = st.text_area("Auxiliares", value=aux_fixa, height=220, key="nova_aux")

with col_c:
    st.markdown("#### Saída para Entrega (hora + ton)")
    entrega_input = st.text_area("Saída para Entrega", value=entrega_fixa, height=220, key="entrega_input",
                                 placeholder="08:00 7,0\n08:20 22,2...")
    st.markdown("#### Retorno de Coleta (hora + ton)")
    coleta_input = st.text_area("Retorno de Coleta", value=coleta_fixa, height=220, key="coleta_input",
                                placeholder="18:00 20,5\n18:45 17,6...")

    st.markdown("#### Opções")
    st.checkbox("Rótulos", value=True, key="rotulos")
    st.checkbox("Mostrar símbolos e barras de Saída/Retorno", value=True, key="mostrar_simbolos")

st.success("Dados de Saída para Entrega e Retorno de Coleta já carregados e visíveis nos campos! 27/11/2025")
