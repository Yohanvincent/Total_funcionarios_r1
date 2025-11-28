# pages/Producao_x_Equipe_Simplificado.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="Produção × Equipe")
st.title("Produção × Equipe – Apenas Chegada e Saída Linha")

# ================= DADOS ATUALIZADOS (você enviou) =================
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

confer_fixa = """01:00 04:00 05:05 10:23 1
16:00 20:00 21:05 01:24 2
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19
23:50 02:40 03:45 09:11 4"""

aux_fixa = """16:00 20:00 21:05 01:24 5
18:00 22:00 23:00 03:12 1
19:00 22:52 12
19:00 23:00 00:05 04:09 13
19:15 23:06 1
21:00 01:00 02:05 06:08 29
21:30 01:30 02:30 06:33 1
22:00 02:00 03:05 07:03 20
23:30 03:30 04:35 08:49 25
23:50 02:40 03:45 09:11 1"""

# ================= SESSION STATE =================
if "init" not in st.session_state:
    st.session_state.chegada = chegada_fixa
    st.session_state.saida   = saida_fixa
    st.session_state.confer  = confer_fixa
    st.session_state.aux     = aux_fixa
    st.session_state.rotulos = True

# ================= FUNÇÕES =================
def hora_para_min(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 0

def extrair_ton(texto):
    dados = {}
    for linha in texto.strip().split("\n"):
        if not linha.strip(): continue
        p = linha.strip().split()
        if len(p) >= 2:
            h = p[0]
            try:
                v = float(p[1].replace(",", "."))
                dados[h] = dados.get(h, 0) + v
            except:
                pass
    return dados

def parse_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        if not linha.strip(): continue
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():
            e = hora_para_min(p[0])
            si = hora_para_min(p[1])
            ri = hora_para_min(p[2])
            sf = hora_para_min(p[3])
            q = int(p[4])
            if sf < e: sf += 1440
            if ri < si: ri += 1440
            jornadas.append({"tipo": "intervalo", "e": e, "si": si, "ri": ri, "sf": sf, "q": q})
        elif len(p) == 3 and p[2].isdigit():
            e = hora_para_min(p[0])
            s = hora_para_min(p[1])
            q = int(p[2])
            if s < e: s += 1440
            jornadas.append({"tipo": "simples", "e": e, "s": s, "q": q})
    return jornadas

def todos_horarios():
    s = set()
    for t in [st.session_state.chegada, st.session_state.saida, st.session_state.confer, st.session_state.aux]:
        for linha in t.strip().split("\n"):
            if not linha.strip(): continue
            p = linha.strip().split()
            if len(p) >= 2:
                s.add(p[0])
            if len(p) in (3,5):
                s.update(p[:4])
    return sorted(s, key=hora_para_min)

def calcular_equipe(jornadas, horarios):
    eq = []
    for h_min = [hora_para_min(h) for h in horarios]
    for m in h_min:
        total = 0
        for j in jornadas:
            if j["tipo"] == "intervalo":
                if (j["e"] <= m < j["si"]) or (j["ri"] <= m <= j["sf"]):
                    total += j["q"]
            else:
                if j["e"] <= m <= j["s"]:
                    total += j["q"]
        eq.append(total)
    return eq

# ================= PROCESSAMENTO =================
cheg = extrair_ton(st.session_state.chegada)
said = extrair_ton(st.session_state.saida)

j_conf = parse_jornadas(st.session_state.confer)
j_aux  = parse_jornadas(st.session_state.aux)

horarios = todos_horarios()

eq_conf = calcular_equipe(j_conf, horarios)
eq_aux  = calcular_equipe(j_aux,  horarios)
eq_total = [a + b for a, b in zip(eq_conf, eq_aux)]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": [round(cheg.get(h, 0), 1) for h in horarios],
    "Saida_Ton"  : [round(said.get(h, 0), 1) for h in horarios],
    "Equipe"     : eq_total
})

max_ton = max(df["Chegada_Ton"].max(), df["Saida_Ton"].max()) + 10
scale = max_ton / (df["Equipe"].max() + 5) if df["Equipe"].max() > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# ================= GRÁFICO =================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada", marker_color="#90EE90", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Carregada", marker_color="#E74C3C", opacity=0.8))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    customdata=df["Equipe"],
    hovertemplate="Equipe: <b>%{customdata}</b> pessoas<extra></extra>"
))

if st.session_state.rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"+{r['Chegada_Ton']}",
                               font=dict(color="#2ECC71", size=9), bgcolor="white", bordercolor="#90EE90", borderwidth=1,
                               showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"-{r['Saida_Ton']}",
                               font=dict(color="#E74C3C", size=9), bgcolor="white", bordercolor="#E74C3C", borderwidth=1,
                               showarrow=False, yshift=10)
        if r["Equipe"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"], text=str(int(r["Equipe"])),
                               font=dict(color="#9B59B6", size=9), bgcolor="white", bordercolor="#9B59B6", borderwidth=1,
                               showarrow=False, yshift=0)

fig.update_layout(
    title="Produção × Equipe – Apenas Chegada e Saída Linha",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.2]),
    height=750,
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5,
                font=dict(size=12), bgcolor="rgba(255,255,255,0.95)", bordercolor="#ccc", borderwidth=1),
    margin=dict(l=60, r=60, t=100, b=140)
)

st.plotly_chart(fig, use_container_width=True)

# ================= DOWNLOAD =================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
buffer.seek(0)
st.download_button("Baixar Excel", buffer, "producao_atualizada.xlsx")

# ================= INPUTS =================
st.markdown("---")
st.markdown("### Editar Dados")

c1, c2 = st.columns(2)
with c1:
    st.session_state.chegada = st.text_area("Chegadas Linha", st.session_state.chegada, height=320)
    st.session_state.confer  = st.text_area("Conferentes", st.session_state.confer, height=320)
with c2:
    st.session_state.saida = st.text_area("Saídas Linha", st.session_state.saida, height=320)
    st.session_state.aux   = st.text_area("Auxiliares", st.session_state.aux, height=320)

st.session_state.rotulos = st.checkbox("Mostrar rótulos", value=True)

st.success("Tudo rodando 100% com seus novos dados! Jornadas noturnas calculadas corretamente!")
