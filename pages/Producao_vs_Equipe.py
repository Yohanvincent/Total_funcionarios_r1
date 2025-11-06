# pages/3_Producao_vs_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("Producao vs Equipe Disponivel")

rotulos = st.checkbox("Rotulos", True)

# --- Upload Producao ---
if "prod_bytes" not in st.session_state:
    st.session_state.prod_bytes = None
if "prod_name" not in st.session_state:
    st.session_state.prod_name = None

padrao_producao = "Cheg. Ton.\n01:00 7,278041\n02:30 6,936955\n03:30 0\n04:00 3,542897\n04:30 1,676141\n05:15 14,263712\n05:30 4,482417\n05:50 3,695104\n06:00 4,389653\n06:00 3,4539\n06:00 2,153276\n06:00 2,852677\n06:30 2,720908\n07:15 6,567569\n07:30 1,44941\n09:30 12,076731\n10:15 0,1992\n11:00 1,462557\n12:45 0\n18:00 6,98727\n21:30 2,837159\n23:30 7,998834\nSaida Ton.\n03:15 5,618428\n04:45 0\n20:15 8,43512\n21:00 0,909347\n21:00 6,061068\n21:00 3,913779\n21:00 4,649687\n21:00 2,756661\n21:00 2,461966\n21:00 1,787873\n21:00 4,040584\n21:00 2,996577\n21:00 4,22898\n21:10 5,479109\n21:20 9,849377\n21:30 5,961456\n21:30 8,997052\n22:00 0,351623\n22:00 0,366688\n22:00 7,782288\n22:15 5,598385\n23:45 18,571689"

def ler_producao(b, f):
    if b is None: return f
    try: return b.decode("utf-8")
    except: 
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)

texto_producao = ler_producao(st.session_state.prod_bytes, padrao_producao)

# --- Upload Equipe (Conferentes + Auxiliares) ---
if "equipe_bytes" not in st.session_state:
    st.session_state.equipe_bytes = None
if "equipe_name" not in st.session_state:
    st.session_state.equipe_name = None

padrao_equipe = """00:00 04:00 05:15 09:33 9
04:00 09:00 10:15 13:07 27
04:30 08:30 10:30 15:14 1
06:00 11:00 12:15 16:03 1
07:45 12:00 13:15 17:48 1
08:00 12:00 13:15 18:03 2
10:00 12:00 14:00 20:48 11
12:00 16:00 17:15 22:02 8
13:00 16:00 17:15 22:55 5
15:45 18:00 18:15 22:00 7
16:30 19:30 19:45 22:39 2
00:00 04:00 05:15 09:33 10
04:00 09:00 10:15 13:07 17
12:00 16:00 17:15 22:02 2
13:00 16:00 17:15 22:55 3
15:45 18:00 18:15 22:00 3
16:30 19:30 19:45 22:39 2
17:48 21:48 1
18:00 22:00 19
19:00 22:52 5"""

def ler_equipe(b, f):
    if b is None: return f
    try: return b.decode("utf-8")
    except: 
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)

texto_equipe = ler_equipe(st.session_state.equipe_bytes, padrao_equipe)

# --- Leitura Producao ---
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
            if modo == "cheg": cheg[h] = cheg.get(h, 0) + v
            else: said[h] = said.get(h, 0) + v
        except: pass
    return cheg, said

cheg, said = extrair_producao(texto_producao)

# --- Leitura Equipe ---
def jornadas(t):
    j = []
    for l in t.strip().split("\n"):
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"t": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return j

def min_hora(h):
    try: h, m = map(int, h.split(":")); return h * 60 + m
    except: return 0

def get_horarios(jc, ja):
    h = {"00:00", "23:59"}
    for t in [jc, ja]:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3, 5): h.update(p[:-1])
    return sorted(h, key=min_hora)

def calcular_equipe(jornadas_list, horarios):
    tl = [min_hora(h) for h in horarios]
    eq = [0] * len(tl)
    for j in jornadas_list:
        e = min_hora(j["e"])
        sf = min_hora(j["sf"])
        if j["t"] == "c":
            si = min_hora(j["si"])
            ri = min_hora(j["ri"])
            for i, t in enumerate(tl):
                if (e <= t < si) or (ri <= t <= sf): eq[i] += j["q"]
        else:
            for i, t in enumerate(tl):
                if e <= t <= sf: eq[i] += j["q"]
    return eq

# Todos os horarios
todas_horas = set(cheg.keys()) | set(said.keys())
jornadas_equipe = jornadas(texto_equipe)
horas_equipe = get_horarios(texto_equipe, "")
todas_horas.update(horas_equipe)
horarios = sorted(todas_horas, key=min_hora)

# Calcula equipe
eq = calcular_equipe(jornadas_equipe, horarios)

# Valores
cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
said_val = [round(said.get(h, 0), 1) for h in horarios]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq
})

# Escala
max_cheg = max(cheg_val) if cheg_val else 0
max_said = max(said_val) if said_val else 0
max_eq = max(eq) if eq else 0
margem = 5
y_max = max(max_cheg, max_said) + margem
eq_range = max_eq + margem
scale = y_max / eq_range if eq_range > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# Gráfico
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#2ECC71", opacity=0.8
))

fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Saida_Ton"],
    name="Saida (ton)", marker_color="#E74C3C", opacity=0.8
))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#9B59B6", width=4),
    marker=dict(size=8),
    yaxis="y"
))

if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"],
                text=f"{r['Chegada_Ton']}", font=dict(color="#2ECC71", size=9),
                bgcolor="white", bordercolor="#2ECC71", borderwidth=1,
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

# --- Uploads ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Upload Producao (Cheg. + Saida)**")
    up_prod = st.file_uploader("TXT/CSV/XLSX", ["txt","csv","xlsx"], key="up_prod")
    if up_prod:
        st.session_state.prod_bytes = up_prod.getvalue()
        st.session_state.prod_name = up_prod.name
    if st.session_state.prod_name:
        st.success(f"Produção: **{st.session_state.prod_name}**")

with col2:
    st.markdown("**Upload Equipe (Conferentes + Auxiliares)**")
    up_eq = st.file_uploader("TXT/CSV/XLSX", ["txt","csv","xlsx"], key="up_eq")
    if up_eq:
        st.session_state.equipe_bytes = up_eq.getvalue()
        st.session_state.equipe_name = up_eq.name
    if st.session_state.equipe_name:
        st.success(f"Equipe: **{st.session_state.equipe_name}**")

# Download
out = io.BytesIO()
df_export = df[["Horario", "Chegada_Ton", "Saida_Ton", "Equipe"]].copy()
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df_export.to_excel(w, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_vs_equipe.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Dados carregados
if st.session_state.prod_name or st.session_state.equipe_name:
    st.markdown("### Dados Carregados")
    if st.session_state.prod_name:
        st.code(texto_producao, language="text")
    if st.session_state.equipe_name:
        st.code(texto_equipe, language="text")

with st.expander("Formato do arquivo - Producao"):
    st.markdown("Cheg. Ton.\n01:00 7,278041\n...\nSaida Ton.\n23:45 18,571689")

with st.expander("Formato do arquivo - Equipe"):
    st.markdown("HH:MM HH:MM HH:MM HH:MM QTD  (jornada com intervalo)\nHH:MM HH:MM QTD  (jornada simples)\n- Uma linha por grupo de colaboradores")
