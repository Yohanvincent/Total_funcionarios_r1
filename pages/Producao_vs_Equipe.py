# pages/3_Producao_vs_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("Producao vs Equipe Disponivel")

rotulos = st.checkbox("Rotulos", True)

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

texto = ler_producao(st.session_state.prod_bytes, padrao_producao)

def extrair(texto):
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

cheg, said = extrair(texto)

# TODAS AS HORAS UNICAS (chegadas + saidas + equipe)
todas = set(cheg.keys()) | set(said.keys())

padrao_conf = "00:00 04:00 05:15 09:33 9\n04:00 09:00 10:15 13:07 27\n04:30 08:30 10:30 15:14 1\n06:00 11:00 12:15 16:03 1\n07:45 12:00 13:15 17:48 1\n08:00 12:00 13:15 18:03 2\n10:00 12:00 14:00 20:48 11\n12:00 16:00 17:15 22:02 8\n13:00 16:00 17:15 22:55 5\n15:45 18:00 18:15 22:00 7\n16:30 19:30 19:45 22:39 2"
padrao_aux = "00:00 04:00 05:15 09:33 10\n04:00 09:00 10:15 13:07 17\n12:00 16:00 17:15 22:02 2\n13:00 16:00 17:15 22:55 3\n15:45 18:00 18:15 22:00 3\n16:30 19:30 19:45 22:39 2\n17:48 21:48 1\n18:00 22:00 19\n19:00 22:52 5"

def jornadas(t):
    j = []
    for l in t.strip().split("\n"):
        p = l.strip().split()
        if len(p)==5 and p[4].isdigit(): j.append({"t":"c","e":p[0],"si":p[1],"ri":p[2],"sf":p[3],"q":int(p[4])})
        elif len(p)==3 and p[2].isdigit(): j.append({"t":"m","e":p[0],"sf":p[1],"q":int(p[2])})
    return j

def min(h):
    try: h,m = map(int, h.split(":")); return h*60 + m
    except: return 0

def horarios(jc, ja):
    h = {"00:00","23:59"}
    for t in [jc,ja]:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3,5): h.update(p[:-1])
    return sorted(h, key=min)

horas_equipe = horarios(padrao_conf, padrao_aux)
todas.update(horas_equipe)
horarios = sorted(todas, key=min)
tl = [min(h) for h in horarios]
eq = [0] * len(tl)

def aplicar(j, lista, tl):
    e = min(j["e"])
    sf = min(j["sf"])
    if j["t"] == "c":
        si = min(j["si"])
        ri = min(j["ri"])
        for i,t in enumerate(tl):
            if (e <= t < si) or (ri <= t <= sf): lista[i] += j["q"]
    else:
        for i,t in enumerate(tl):
            if e <= t <= sf: lista[i] += j["q"]

for j in jornadas(padrao_conf): aplicar(j, eq, tl)
for j in jornadas(padrao_aux): aplicar(j, eq, tl)

# VALORES EXATOS POR HORA (1 casa decimal)
cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
said_val = [round(said.get(h, 0), 1) for h in horarios]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq
})

fig = go.Figure()

# Barras: Chegada (verde)
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#2ECC71", opacity=0.8
))

# Barras: Saida (vermelho)
fig.add_trace(go.Bar(
    x=df["Horario"], y=-df["Saida_Ton"],  # negativo para baixo
    name="Saida (ton)", marker_color="#E74C3C", opacity=0.8
))

# Linha: Equipe
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#4ECDC4", width=4), yaxis="y2"
))

if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"<b>{r['Chegada_Ton']}</b>", showarrow=False, font=dict(color="#2ECC71", size=9), yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=-r["Saida_Ton"], text=f"<b>{r['Saida_Ton']}</b>", showarrow=False, font=dict(color="#E74C3C", size=9), yshift=-10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe"], text=f"<b>{int(r['Equipe'])}</b>", showarrow=False, font=dict(color="#4ECDC4", size=9), yshift=10)

fig.update_layout(
    xaxis_title="Horario",
    yaxis=dict(title="Toneladas (Chegada + / Saida -)", side="left"),
    yaxis2=dict(title="Equipe", side="right", overlaying="y"),
    height=600,
    hovermode="x unified",
    legend=dict(x=0, y=1.1, orientation="h"),
    barmode="relative"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**Upload Producao (Cheg. + Saida) ou use padrao.**")
up = st.file_uploader("TXT/CSV/XLSX", ["txt","csv","xlsx"], key="up")
if up:
    st.session_state.prod_bytes = up.getvalue()
    st.session_state.prod_name = up.name
if st.session_state.prod_name:
    st.success(f"Arquivo: **{st.session_state.prod_name}**")

out = io.BytesIO()
with pd.ExcelWriter(out, engine="openpyxl") as w: df.to_excel(w, index=False)
out.seek(0)
st.download_button("Baixar Excel", out, "producao_detalhada.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if st.session_state.prod_name:
    st.markdown("### Dados Carregados")
    st.code(texto, language="text")

with st.expander("Formato do arquivo"):
    st.markdown("Cheg. Ton.\n01:00 7,278041\n...\nSaida Ton.\n23:45 18,571689\n- HH:MM valor\n- Virgula ou ponto\n- Multiplas linhas somadas")
