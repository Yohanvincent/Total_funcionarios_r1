# pages/Acumulado_x_Producao.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# -------------------------------------------------
# CONFIGURAÇÃO
# -------------------------------------------------
st.set_page_config(layout="wide")
st.title("📦 Capacidade × Produção × Acumulado × Funcionários")

rotulos = st.checkbox("Exibir rótulos", True)

# -------------------------------------------------
# SESSION STATE (persistência dos uploads)
# -------------------------------------------------
keys = ["chegadas_bytes", "saidas_bytes", "conf_bytes", "aux_bytes", "capacidade_bytes",
        "chegadas_name", "saidas_name", "conf_name", "aux_name", "capacidade_name"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None

# -------------------------------------------------
# DADOS PADRÃO (exemplo que você passou)
# -------------------------------------------------
padrao_chegadas = """00:00 1,7
00:00 6,3
... (resto do seu bloco de chegadas) ..."""

padrao_saidas = """00:00 0,1
... (resto das saídas) ..."""

padrao_conf = """01:00 04:00 05:05 10:23 1
... (jornadas conferentes) ..."""

padrao_aux = """16:00 20:00 21:05 01:24 5
... (jornadas auxiliares) ..."""

padrao_capacidade = """00:00 4.779
01:00 3.197
... (capacidade por hora) ..."""

# -------------------------------------------------
# FUNÇÕES AUXILIARES
# -------------------------------------------------
def ler_bytes(b, fallback):
    if b is None: return fallback
    try: return b.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)

def min_hora(h):
    try: return sum(int(x) * (60 ** i) for i, x in enumerate(reversed(h.split(":"))))
    except: return 0

def extrair_movimentos(texto):
    d = {}
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) >= 2:
            h, v = p[0], p[1].replace(",", ".")
            try: d[h] = d.get(h, 0) + float(v)
            except: pass
    return d

def extrair_jornadas(texto):
    j = []
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({"e":p[0],"si":p[1],"ri":p[2],"sf":p[3],"q":int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"e":p[0],"sf":p[1],"q":int(p[2])})
    return j

def extrair_capacidade(texto):
    c = {}
    for l in texto.strip().splitlines():
        p = l.strip().split()
        if len(p) >= 2:
            h, v = p[0], p[1].replace(",", ".")
            try: c[h] = float(v)
            except: pass
    return c

def floor_hour(h):
    hh = str(min_hora(h) // 60).zfill(2)
    return f"{hh}:00"

# -------------------------------------------------
# CARREGAR DADOS
# -------------------------------------------------
chegadas_txt = ler_bytes(st.session_state.chegadas_bytes, padrao_chegadas)
saidas_txt   = ler_bytes(st.session_state.saidas_bytes,   padrao_saidas)
conf_txt     = ler_bytes(st.session_state.conf_bytes,     padrao_conf)
aux_txt      = ler_bytes(st.session_state.aux_bytes,      padrao_aux)
cap_txt      = ler_bytes(st.session_state.capacidade_bytes, padrao_capacidade)

cheg = extrair_movimentos(chegadas_txt)
said = extrair_movimentos(saidas_txt)
capacidade_hora = extrair_capacidade(cap_txt)

# -------------------------------------------------
# TODAS AS HORAS ÚNICAS
# -------------------------------------------------
horas_set = set(cheg.keys()) | set(said.keys()) | set(capacidade_hora.keys())
for txt in [conf_txt, aux_txt]:
    for l in txt.splitlines():
        p = l.split()
        if len(p) >= 4: horas_set.update(p[:4])
horarios = sorted(horas_set, key=min_hora)

# -------------------------------------------------
# FUNCIONÁRIOS POR HORÁRIO
# -------------------------------------------------
timeline_min = [min_hora(h) for h in horarios]
func_total = [0] * len(horarios)

def aplicar_jornada(j, tl):
    e = min_hora(j["e"])
    sf = min_hora(j["sf"])
    if "si" in j:
        si = min_hora(j["si"])
        ri = min_hora(j["ri"])
        for i, t in enumerate(tl):
            if (e <= t < si) or (ri <= t <= sf):
                func_total[i] += j["q"]
    else:
        for i, t in enumerate(tl):
            if e <= t <= sf:
                func_total[i] += j["q"]

for j in extrair_jornadas(conf_txt): aplicar_jornada(j, timeline_min)
for j in extrair_jornadas(aux_txt):   aplicar_jornada(j, timeline_min)

# -------------------------------------------------
# DATAFRAME FINAL – **tudo em toneladas**
# -------------------------------------------------
df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_ton":   [round(cheg.get(h, 0), 1) for h in horarios],
    "Saida_ton":     [round(said.get(h, 0), 1) for h in horarios],
    "Funcionarios":  func_total,
    "Capacidade_ton":[round(capacidade_hora.get(floor_hour(h), 0), 3) for h in horarios],
})
df["Acumulado_ton"] = (df["Chegada_ton"] - df["Saida_ton"]).cumsum().round(1)

# -------------------------------------------------
# GRÁFICO – **mesmo eixo Y** (toneladas)
# -------------------------------------------------
fig = go.Figure()

# 1. Barras empilhadas (chegada + saída)
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Chegada_ton"],
    name="Chegada (ton)", marker_color="#2ca02c", opacity=0.85
))
fig.add_trace(go.Bar(
    x=df["Horario"], y=df["Saida_ton"],
    name="Saída (ton)", marker_color="#d62728", opacity=0.85
))

# 2. Capacidade (degrau)
x_step, y_step = [], []
for i, row in df.iterrows():
    x_step.append(row["Horario"])
    y_step.append(row["Capacidade_ton"])
    if i < len(df) - 1:
        x_step.extend([row["Horario"], df.iloc[i+1]["Horario"]])
        y_step.extend([row["Capacidade_ton"], row["Capacidade_ton"]])
fig.add_trace(go.Scatter(
    x=x_step, y=y_step,
    mode="lines", name="Capacidade (ton)",
    line=dict(color="#9B59B6", width=4),
    hovertemplate="%{y:.3f} ton"
))

# 3. Acumulado (área)
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Acumulado_ton"],
    mode="lines", name="Acumulado (ton)",
    fill="tozeroy", fillcolor="rgba(148,103,189,0.3)",
    line=dict(color="#9467bd", width=3),
    hovertemplate="%{y:.1f} ton"
))

# 4. Funcionários (linha fina – **mesmo eixo**)
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Funcionarios"],
    mode="lines+markers", name="Funcionários",
    line=dict(color="#1f77b4", width=2, dash="dot"),
    marker=dict(size=4),
    hovertemplate="%{y} pessoas"
))

# -------------------------------------------------
# RÓTULOS (valor real, 1 casa decimal)
# -------------------------------------------------
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_ton"],
                               text=f"{r['Chegada_ton']:.1f}",
                               font=dict(color="white", size=9),
                               bgcolor="#2ca02c", showarrow=False, yshift=8)
        if r["Saida_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=r["Saida_ton"],
                               text=f"{r['Saida_ton']:.1f}",
                               font=dict(color="white", size=9),
                               bgcolor="#d62728", showarrow=False, yshift=8)

# -------------------------------------------------
# LAYOUT (único eixo Y)
# -------------------------------------------------
max_y = max(df[["Capacidade_ton","Acumulado_ton","Chegada_ton","Saida_ton"]].max()) * 1.15
max_func = df["Funcionarios"].max()

fig.update_layout(
    title="Análise Unificada – Todas as métricas em **toneladas**",
    xaxis_title="Horário",
    yaxis=dict(
        title="Toneladas (ou pessoas – mesma escala)",
        range=[0, max(max_y, max_func*1.2)]   # garante que funcionários caibam
    ),
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=720,
    margin=dict(l=70, r=70, t=90, b=60),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# UPLOADS
# -------------------------------------------------
st.markdown("### Upload de arquivos")
cols = st.columns(5)
with cols[0]:
    up = st.file_uploader("Chegadas", ["txt","csv","xlsx"], key="c")
    if up: st.session_state.chegadas_bytes, st.session_state.chegadas_name = up.getvalue(), up.name
    if st.session_state.chegadas_name: st.success(st.session_state.chegadas_name)
with cols[1]:
    up = st.file_uploader("Saídas", ["txt","csv","xlsx"], key="s")
    if up: st.session_state.saidas_bytes, st.session_state.saidas_name = up.getvalue(), up.name
    if st.session_state.saidas_name: st.success(st.session_state.saidas_name)
with cols[2]:
    up = st.file_uploader("Conferentes", ["txt","csv","xlsx"], key="conf")
    if up: st.session_state.conf_bytes, st.session_state.conf_name = up.getvalue(), up.name
    if st.session_state.conf_name: st.success(st.session_state.conf_name)
with cols[3]:
    up = st.file_uploader("Auxiliares", ["txt","csv","xlsx"], key="aux")
    if up: st.session_state.aux_bytes, st.session_state.aux_name = up.getvalue(), up.name
    if st.session_state.aux_name: st.success(st.session_state.aux_name)
with cols[4]:
    up = st.file_uploader("Capacidade", ["txt","csv","xlsx"], key="cap")
    if up: st.session_state.capacidade_bytes, st.session_state.capacidade_name = up.getvalue(), up.name
    if st.session_state.capacidade_name: st.success(st.session_state.capacidade_name)

# -------------------------------------------------
# TABELA + DOWNLOAD
# -------------------------------------------------
with st.expander("Tabela completa (toneladas)"):
    df_disp = df.copy()
    df_disp["Capacidade_ton"] = df_disp["Capacidade_ton"].map("{:.3f}".format)
    df_disp["Chegada_ton"]   = df_disp["Chegada_ton"].map("{:.1f}".format)
    df_disp["Saida_ton"]     = df_disp["Saida_ton"].map("{:.1f}".format)
    df_disp["Acumulado_ton"] = df_disp["Acumulado_ton"].map("{:.1f}".format)
    st.dataframe(df_disp, use_container_width=True)

    csv = df.to_csv(index=False).encode()
    st.download_button("Baixar CSV", csv, "dados_unificados_ton.csv", "text/csv")
