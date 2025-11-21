# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("🚛 Produção vs Equipe Disponível + Janelas Críticas")

rotulos = st.checkbox("Rótulos", value=True)
mostrar_simbolos = st.checkbox("Mostrar símbolos Saída Entrega / Retorno Coleta", value=True)

# ==============================================================
# 1 – ENTRADA DE DADOS
# ==============================================================
st.markdown("### ✏️ Cole novos dados (opcional – substitui os fixos)")

col_a, col_b, col_c = st.columns([2, 2, 1.8])

with col_a:
    nova_chegada = st.text_area("Chegadas (horário tonelada – uma por linha)", height=200,
                                placeholder="04:30 15.8\n05:00 12.4")
    nova_confer = st.text_area("Conferentes (entrada saída_int retorno_int saída_final qtd)", height=200)

with col_b:
    nova_saida = st.text_area("Saídas (horário tonelada – uma por linha)", height=200)
    nova_aux = st.text_area("Auxiliares (entrada saída qtd)", height=200)

with col_c:
    st.markdown("#### Horários Críticos")
    st.info("⚠️ Agora você pode colar apenas as horas (uma por linha) em cada campo")
    
    col_ret, col_ent = st.columns(2)
    with col_ret:
        retorno_input = st.text_area("Retorno de Coleta (só horário)", height=280,
                                     placeholder="18:00\n18:15\n18:30")
    with col_ent:
        entrega_input = st.text_area("Saída para Entrega (só horário)", height=280,
                                     placeholder="07:40\n08:00\n14:00")

# ==============================================================
# 2 – DADOS FIXOS
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
# 3 – SUBSTITUIÇÃO DOS DADOS
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_fixa
saida_txt   = nova_saida.strip()   if nova_saida.strip()   else saida_fixa
confer_txt  = nova_confer.strip()  if nova_confer.strip()  else confer_fixa
aux_txt     = nova_aux.strip()     if nova_aux.strip()     else aux_fixa

texto_producao = f"Cheg. Ton.\n{chegada_txt}\nSaida Ton.\n{saida_txt}"
texto_confer = confer_txt
texto_aux = aux_txt

# Horários críticos – agora aceita só a hora
retorno_coleta_hrs = [h.strip() for h in retorno_input.split("\n") if h.strip() and ":" in h]
saida_entrega_hrs = [h.strip() for h in entrega_input.split("\n") if h.strip() and ":" in h]

# ==============================================================
# 4 – RESTO DO CÓDIGO ORIGINAL (100% mantido)
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

jornadas_conf = jornadas(texto_confer)
jornadas_aux = jornadas(texto_aux)

todas_horas = set(cheg.keys()) | set(said.keys())
todas_horas.update(retorno_coleta_hrs + saida_entrega_hrs)
horas_equipe = get_horarios_from_texts(texto_confer, texto_aux)
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

eq_conf = calcular_equipe(jornadas_conf, horarios)
eq_aux = calcular_equipe(jornadas_aux, horarios)
eq_total = [c + a for c, a in zip(eq_conf, eq_aux)]

cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
said_val = [round(said.get(h, 0), 1) for h in horarios]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq_total,
    "Equipe_Conf": eq_conf,
    "Equipe_Aux": eq_aux
})

# Escala equipe
max_cheg = max(cheg_val) if cheg_val else 0
max_said = max(said_val) if said_val else 0
max_eq = max(df["Equipe"]) if len(df) else 0
margem = 5
y_max = max(max_cheg, max_said) + margem
eq_range = max_eq + margem
scale = y_max / eq_range if eq_range > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# ==============================================================
# GRÁFICO
# ==============================================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada (ton)", marker_color="#90EE90", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída (ton)", marker_color="#E74C3C", opacity=0.8))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# SÍMBOLOS CORRIGIDOS: SAÍDA ENTREGA ▲ (para cima) | RETORNO COLETA ▼ (para baixo)
if mostrar_simbolos:
    if saida_entrega_hrs:
        fig.add_trace(go.Scatter(
            x=saida_entrega_hrs,
            y=[y_max * 1.08] * len(saida_entrega_hrs),
            mode="markers",
            marker=dict(color="#2980B9", size=20, symbol="triangle-up"),  # ▲ para cima
            name="Saída para Entrega",
            hoverinfo="none"
        ))
    if retorno_coleta_hrs:
        fig.add_trace(go.Scatter(
            x=retorno_coleta_hrs,
            y=[y_max * 1.08] * len(retorno_coleta_hrs),
            mode="markers",
            marker=dict(color="#E67E22", size=20, symbol="triangle-down"),  # ▼ para baixo
            name="Retorno de Coleta",
            hoverinfo="none"
        ))

# RÓTULOS COM + E -
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"+{r['Chegada_Ton']}",
                               font=dict(color="#2ECC71", size=9), bgcolor="white",
                               bordercolor="#90EE90", borderwidth=1, showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"-{r['Saida_Ton']}",
                               font=dict(color="#E74C3C", size=9), bgcolor="white",
                               bordercolor="#E74C3C", borderwidth=1, showarrow=False, yshift=10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"], text=f"{int(r['Equipe'])}",
                               font=dict(color="#9B59B6", size=9), bgcolor="white",
                               bordercolor="#9B59B6", borderwidth=1, showarrow=False, yshift=0, align="center")

fig.update_layout(
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", side="left", range=[0, y_max * 1.15], zeroline=False),
    height=700,
    hovermode="x unified",
    legend=dict(x=0, y=1.1, orientation="h"),
    barmode="stack",
    margin=dict(l=60, r=60, t=80, b=60)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# DOWNLOAD
# ==============================================================
out = io.BytesIO()
df_export = df[["Horario", "Chegada_Ton", "Saida_Ton", "Equipe", "Equipe_Conf", "Equipe_Aux"]].copy()
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df_export.to_excel(w, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_vs_equipe.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.success("Atualizado com sucesso! Triângulos corrigidos + agora aceita só horário nos campos críticos – 21/11/2025 ✅")
