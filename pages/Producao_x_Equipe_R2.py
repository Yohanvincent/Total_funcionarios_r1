# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("Produção vs Equipe Disponível")

rotulos = st.checkbox("Rótulos", True)

# ==============================================================
# 1 – OPÇÃO DE COLAR DADOS (SOBRESCREVE OS FIXOS)
# ==============================================================
st.markdown("### ✏️ Cole novos dados (opcional – substitui os fixos)")

col_a, col_b = st.columns(2)

with col_a:
    nova_chegada = st.text_area(
        "Chegadas (horário tonelada – uma por linha)",
        height=200,
        placeholder="04:30 15.8\n05:00 12.4\n..."
    )
    nova_confer = st.text_area(
        "Conferentes (entrada saída_int retorno_int saída_final qtd)",
        height=200,
        placeholder="04:30 09:30 10:30 13:26 2\n19:00 23:00 00:05 04:09 8\n..."
    )

with col_b:
    nova_saida = st.text_area(
        "Saídas (horário tonelada – uma por linha)",
        height=200,
        placeholder="06:00 14.4\n07:00 15.9\n..."
    )
    nova_aux = st.text_area(
        "Auxiliares (entrada saída qtd)",
        height=200,
        placeholder="19:00 04:09 13\n21:00 06:08 29\n..."
    )

# ==============================================================
# 2 – DADOS FIXOS (usados se nada for colado)
# ==============================================================
chegada_fixa = """00:00 1,7
00:00 6,3
00:20 14,9
... (seu texto completo aqui) ...
23:20 8,2"""

saida_fixa = """00:00 0,1
00:30 1,4
... (seu texto completo aqui) ...
23:30 0,6"""

confer_fixa = """01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
... (todo o bloco original) ..."""

aux_fixa = """16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
... (todo o bloco original) ..."""

# ==============================================================
# 3 – SUBSTITUIÇÃO DOS DADOS (se o usuário colar algo)
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_fixa
saida_txt   = nova_saida.strip()   if nova_saida.strip()   else saida_fixa
confer_txt  = nova_confer.strip()  if nova_confer.strip()  else confer_fixa
aux_txt     = nova_aux.strip()     if nova_aux.strip()     else aux_fixa

texto_producao = f"Cheg. Ton.\n{chegada_txt}\nSaida Ton.\n{saida_txt}"
texto_confer   = confer_txt
texto_aux      = aux_txt

# ==============================================================
# 4 – O RESTO DO CÓDIGO É EXATAMENTE O ORIGINAL (sem nenhuma alteração)
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
jornadas_aux  = jornadas(texto_aux)

todas_horas   = set(cheg.keys()) | set(said.keys())
horas_equipe  = get_horarios_from_texts(texto_confer, texto_aux)
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
eq_aux  = calcular_equipe(jornadas_aux, horarios)
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

# Escala (exatamente como estava)
max_cheg = max(cheg_val) if cheg_val else 0
max_said = max(said_val) if said_val else 0
max_eq   = max(df["Equipe"]) if len(df) else 0
margem   = 5
y_max    = max(max_cheg, max_said) + margem
eq_range = max_eq + margem
scale    = y_max / eq_range if eq_range > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# ==============================================================
# GRÁFICO – 100% ORIGINAL
# ==============================================================
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#90EE90", opacity=0.8
))
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Saida_Ton"],
    name="Saída (ton)", marker_color="#E74C3C", opacity=0.8
))
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"{r['Chegada_Ton']}",
                               font=dict(color="#2ECC71", size=9), bgcolor="white",
                               bordercolor="#90EE90", borderwidth=1, showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"{r['Saida_Ton']}",
                               font=dict(color="#E74C3C", size=9), bgcolor="white",
                               bordercolor="#E74C3C", borderwidth=1, showarrow=False, yshift=10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"], text=f"{int(r['Equipe'])}",
                               font=dict(color="#9B59B6", size=9), bgcolor="white",
                               bordercolor="#9B59B6", borderwidth=1, showarrow=False, yshift=0, align="center")

fig.update_layout(
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", side="left", range=[0, y_max], zeroline=False),
    height=650, hovermode="x unified", legend=dict(x=0, y=1.1, orientation="h"),
    barmode="stack", margin=dict(l=60, r=60, t=40, b=60)
)
st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# DOWNLOAD EXCEL
# ==============================================================
out = io.BytesIO()
df_export = df[["Horario", "Chegada_Ton", "Saida_Ton", "Equipe", "Equipe_Conf", "Equipe_Aux"]].copy()
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df_export.to_excel(w, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_vs_equipe.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ==============================================================
# DADOS UTILIZADOS (mostra o que está ativo)
# ==============================================================
st.markdown("### Dados atualmente em uso")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Chegadas**"); st.code(chegada_txt, language="text")
    st.markdown("**Conferentes**"); st.code(confer_txt, language="text")
with c2:
    st.markdown("**Saídas**"); st.code(saida_txt, language="text")
    st.markdown("**Auxiliares**"); st.code(aux_txt, language="text")
