# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("Producao vs Equipe Disponivel")
rotulos = st.checkbox("Rotulos", True)

# --- Session state defaults para uploads ---
if "prod_bytes" not in st.session_state:
    st.session_state.prod_bytes = None
if "prod_name" not in st.session_state:
    st.session_state.prod_name = None
if "conf_bytes" not in st.session_state:
    st.session_state.conf_bytes = None
if "conf_name" not in st.session_state:
    st.session_state.conf_name = None
if "aux_bytes" not in st.session_state:
    st.session_state.aux_bytes = None
if "aux_name" not in st.session_state:
    st.session_state.aux_name = None

# --- Session state para colagem ---
if "colar_conf" not in st.session_state:
    st.session_state.colar_conf = ""
if "colar_aux" not in st.session_state:
    st.session_state.colar_aux = ""
if "colar_cheg" not in st.session_state:
    st.session_state.colar_cheg = ""
if "colar_said" not in st.session_state:
    st.session_state.colar_said = ""

# --- Padrões ---
padrao_producao = "Cheg. Ton.\n01:00 7,278041\n02:30 6,936955\n03:30 0\n04:00 3,542897\n04:30 1,676141\n05:15 14,263712\n05:30 4,482417\n05:50 3,695104\n06:00 4,389653\n06:00 3,4539\n06:00 2,153276\n06:00 2,852677\n06:30 2,720908\n07:15 6,567569\n07:30 1,44941\n09:30 12,076731\n10:15 0,1992\n11:00 1,462557\n12:45 0\n18:00 6,98727\n21:30 2,837159\n23:30 7,998834\nSaida Ton.\n03:15 5,618428\n04:45 0\n20:15 8,43512\n21:00 0,909347\n21:00 6,061068\n21:00 3,913779\n21:00 4,649687\n21:00 2,756661\n21:00 2,461966\n21:00 1,787873\n21:00 4,040584\n21:00 2,996577\n21:00 4,22898\n21:10 5,479109\n21:20 9,849377\n21:30 5,961456\n21:30 8,997052\n22:00 0,351623\n22:00 0,366688\n22:00 7,782288\n22:15 5,598385\n23:45 18,571689"
padrao_confer = """01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19
23:50 02:40 03:45 09:11 4"""
padrao_aux = """16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
19:00 22:52 12
19:00 23:00 00:05 04:09 13
19:15 23:06 1
21:00 01:00 02:05 06:08 29
21:30 01:30 02:30 06:33 1
22:00 02:00 03:05 07:03 20
23:30 03:30 04:35 08:49 25
23:50 02:40 03:45 09:11 1"""

def ler_texto_bytes(b, f):
    if b is None:
        return f
    try:
        return b.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)

# --- PRIORIDADE: Colar → Upload → Padrão ---
texto_confer = st.session_state.colar_conf.strip() or ler_texto_bytes(st.session_state.conf_bytes, padrao_confer)
texto_aux = st.session_state.colar_aux.strip() or ler_texto_bytes(st.session_state.aux_bytes, padrao_aux)

producao_colada = ""
if st.session_state.colar_cheg.strip():
    producao_colada += "Cheg. Ton.\n" + st.session_state.colar_cheg.strip()
if st.session_state.colar_said.strip():
    if producao_colada:
        producao_colada += "\nSaida Ton.\n" + st.session_state.colar_said.strip()
    else:
        producao_colada = "Cheg. Ton.\n\nSaida Ton.\n" + st.session_state.colar_said.strip()
texto_producao = producao_colada or ler_texto_bytes(st.session_state.prod_bytes, padrao_producao)

# --- Leitura Producao ---
def extrair_producao(texto):
    cheg = {}
    said = {}
    modo = None
    for l in texto.strip().split("\n"):
        l = l.strip()
        if l == "Cheg. Ton.":
            modo = "cheg"
            continue
        if l == "Saida Ton.":
            modo = "said"
            continue
        if not l or modo is None:
            continue
        p = l.split()
        if len(p) < 2:
            continue
        h = p[0]
        try:
            v = float(p[1].replace(",", "."))
            if modo == "cheg":
                cheg[h] = cheg.get(h, 0) + v
            else:
                said[h] = said.get(h, 0) + v
        except:
            pass
    return cheg, said
cheg, said = extrair_producao(texto_producao)

# --- Leitura Jornadas ---
def jornadas(t):
    j = []
    for l in t.strip().split("\n"):
        p = l.strip().split()
        if not p:
            continue
        if len(p) == 5 and p[4].isdigit():
            j.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"t": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return j

def min_hora(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 0

def get_horarios_from_texts(*texts):
    h = {"00:00", "23:59"}
    for t in texts:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3, 5):
                h.update(p[:-1])
    return sorted(h, key=min_hora)

jornadas_conf = jornadas(texto_confer)
jornadas_aux = jornadas(texto_aux)

todas_horas = set(cheg.keys()) | set(said.keys())
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

# Escala
max_cheg = max(cheg_val) if cheg_val else 0
max_said = max(said_val) if said_val else 0
max_eq = max(df["Equipe"]) if len(df) else 0
margem = 5
y_max = max(max_cheg, max_said) + margem
eq_range = max_eq + margem
scale = y_max / eq_range if eq_range > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# --- GRÁFICO (CORRIGIDO: SAÍDA = VERMELHO) ---
fig = go.Figure()
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#90EE90", opacity=0.8
))
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Saida_Ton"],
    name="Saída (ton)", marker_color="#E74C3C", opacity=0.8  # CORRIGIDO: VERMELHO
))
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    customdata=df["Equipe"],
    hovertemplate="Equipe: %{customdata}<extra></extra>",
    showlegend=True
))

if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"],
                text=f"{r['Chegada_Ton']}", font=dict(color="#2ECC71", size=9),
                bgcolor="white", bordercolor="#90EE90", borderwidth=1,
                showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"],
                text=f"{r['Saida_Ton']}", font=dict(color="#E74C3C", size=9),
                bgcolor="white", bordercolor="#E74C3C", borderwidth=1,
                showarrow=False, yshift=10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"],
                text=f"{int(r['Equipe'])}", font=dict(color="#9B59B6", size=9),
                bgcolor="white", bordercolor="#9B59B6", borderwidth=1,
                showarrow=False, yshift=0, align="center", valign="middle")

fig.update_layout(
    xaxis_title="Horario",
    yaxis=dict(title="Toneladas | Equipe (escalada)", side="left", range=[0, y_max], zeroline=False),
    height=650, hovermode="x unified", legend=dict(x=0, y=1.1, orientation="h"),
    barmode="stack", margin=dict(l=60, r=60, t=40, b=60)
)
st.plotly_chart(fig, use_container_width=True)

# --- UPLOADS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Upload Producao (Cheg. + Saida)**")
    up_prod = st.file_uploader("TXT/CSV/XLSX", ["txt","csv","xlsx"], key="up_prod")
    if up_prod:
        st.session_state.prod_bytes = up_prod.getvalue()
        st.session_state.prod_name = up_prod.name
    if st.session_state.prod_name:
        st.success(f"Produção: **{st.session_state.prod_name}**")
with col2:
    st.markdown("**Upload Conferentes**")
    up_conf = st.file_uploader("TXT/CSV/XLSX", ["txt","csv","xlsx"], key="up_conf")
    if up_conf:
        st.session_state.conf_bytes = up_conf.getvalue()
        st.session_state.conf_name = up_conf.name
    if st.session_state.conf_name:
        st.success(f"Conferentes: **{st.session_state.conf_name}**")
with col3:
    st.markdown("**Upload Auxiliares**")
    up_aux = st.file_uploader("TXT/CSV/XLSX", ["txt","csv","xlsx"], key="up_aux")
    if up_aux:
        st.session_state.aux_bytes = up_aux.getvalue()
        st.session_state.aux_name = up_aux.name
    if st.session_state.aux_name:
        st.success(f"Auxiliares: **{st.session_state.aux_name}**")

# --- CAMPOS PARA COLAR ---
st.markdown("### Ou cole os dados diretamente")

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Conferentes (CD Chapecó)**")
    conf_input = st.text_area("Cole aqui", value=st.session_state.colar_conf, height=180, key="conf_colar")
    if conf_input != st.session_state.colar_conf:
        st.session_state.colar_conf = conf_input
        st.success("Conferentes colados!")

    st.markdown("**Produção - Chegada**")
    cheg_input = st.text_area("HH:MM valor", value=st.session_state.colar_cheg, height=180, key="cheg_colar")
    if cheg_input != st.session_state.colar_cheg:
        st.session_state.colar_cheg = cheg_input
        st.success("Chegada colada!")

with c2:
    st.markdown("**Auxiliares**")
    aux_input = st.text_area("Cole aqui", value=st.session_state.colar_aux, height=180, key="aux_colar")
    if aux_input != st.session_state.colar_aux:
        st.session_state.colar_aux = aux_input
        st.success("Auxiliares colados!")

    st.markdown("**Produção - Saída**")
    said_input = st.text_area("HH:MM valor", value=st.session_state.colar_said, height=180, key="said_colar")
    if said_input != st.session_state.colar_said:
        st.session_state.colar_said = said_input
        st.success("Saída colada!")

# --- BAIXAR EXCEL ---
out = io.BytesIO()
df_export = df[["Horario", "Chegada_Ton", "Saida_Ton", "Equipe", "Equipe_Conf", "Equipe_Aux"]].copy()
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df_export.to_excel(w, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_vs_equipe.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- DADOS CARREGADOS ---
if st.session_state.prod_name or st.session_state.conf_name or st.session_state.aux_name or st.session_state.colar_cheg or st.session_state.colar_said:
    st.markdown("### Dados Carregados")
    if st.session_state.prod_name:
        st.code(texto_producao, language="text")
    if st.session_state.conf_name or st.session_state.colar_conf:
        st.code(texto_confer, language="text")
    if st.session_state.aux_name or st.session_state.colar_aux:
        st.code(texto_aux, language="text")

# --- EXPANDERS ---
with st.expander("Formato do arquivo - Producao"):
    st.markdown("Cheg. Ton.\n01:00 7,278041\n...\nSaida Ton.\n23:45 18,571689")
with st.expander("Formato do arquivo - Conferentes"):
    st.markdown("HH:MM HH:MM HH:MM HH:MM QTD (jornada com intervalo)\nHH:MM HH:MM QTD (jornada simples)\n- Uma linha por grupo de colaboradores")
with st.expander("Formato do arquivo - Auxiliares"):
    st.markdown("HH:MM HH:MM HH:MM HH:MM QTD (jornada com intervalo)\nHH:MM HH:MM QTD (jornada simples)\n- Uma linha por grupo de colaboradores")
