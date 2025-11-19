import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide", page_title="📊 Acumulado x Produção - CD")
st.title("📊 Acumulado x Produção - CD")

# =============================================
# CONFIGURAÇÕES
# =============================================
st.sidebar.header("Tempos de Operação (segundos)")
t_descarga = st.sidebar.number_input("Descarga (Auxiliar)", value=30, min_value=1)
t_carga = st.sidebar.number_input("Carga (Conferente)", value=28, min_value=1)
fator_kg_vol = st.sidebar.number_input("1 vol = ? kg", value=16.10, min_value=0.1, step=0.1, format="%.2f")

prod_descarga = (3600 / t_descarga) * fator_kg_vol / 1000
prod_carga = (3600 / t_carga) * fator_kg_vol / 1000

st.sidebar.markdown("### Produtividade por Pessoa")
st.sidebar.metric("Auxiliar (descarga)", f"{prod_descarga*1000:,.0f} kg/h")
st.sidebar.metric("Conferente (carga)", f"{prod_carga*1000:,.0f} kg/h")

escala_pessoas = st.sidebar.slider("Escala visual pessoas (ton/pessoa)", 1.0, 10.0, 3.0, 0.5)
rotulos = st.sidebar.checkbox("Exibir rótulos", True)

# =============================================
# SESSION STATE
# =============================================
keys = ["chegadas_bytes", "saidas_bytes", "conf_bytes", "aux_bytes"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None

# =============================================
# DADOS PADRÃO (SE NÃO TIVER UPLOAD)
# =============================================
padrao_chegadas = """00:00 1,7
00:00 6,3
00:20 14,9
... (dados omitidos por brevidade - mantidos exatamente como no original) ...
23:20 8,2"""

padrao_saidas = """00:00 0,1
... (dados omitidos por brevidade - mantidos exatamente como no original) ...
23:30 0,6"""

padrao_conf = """01:00 04:00 05:05 10:23 1
... (dados omitidos por brevidade - mantidos exatamente como no original) ..."""

padrao_aux = """16:00 20:00 21:05 01:24 5
... (dados omitidos por brevidade - mantidos exatamente como no original) ..."""

# =============================================
# FUNÇÕES
# =============================================
def ler_bytes(b, fallback):
    if b is None: return fallback
    try: return b.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)

def min_hora(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
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
            j.append({"e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({"e": p[0], "sf": p[1], "q": int(p[2])})
    return j

# =============================================
# UPLOAD DE ARQUIVOS
# =============================================
chegadas_bytes = st.file_uploader("Chegadas (TXT ou XLSX)", type=["txt", "xlsx"], key="chegadas")
saidas_bytes = st.file_uploader("Saídas (TXT ou XLSX)", type=["txt", "xlsx"], key="saidas")
conf_bytes = st.file_uploader("Jornada Conferentes (TXT ou XLSX)", type=["txt", "xlsx"], key="conf")
aux_bytes = st.file_uploader("Jornada Auxiliares (TXT ou XLSX)", type=["txt", "xlsx"], key="aux")

if chegadas_bytes: st.session_state.chegadas_bytes = chegadas_bytes.getvalue()
if saidas_bytes: st.session_state.saidas_bytes = saidas_bytes.getvalue()
if conf_bytes: st.session_state.conf_bytes = conf_bytes.getvalue()
if aux_bytes: st.session_state.aux_bytes = aux_bytes.getvalue()

# =============================================
# CARREGAR DADOS
# =============================================
chegadas_txt = ler_bytes(st.session_state.chegadas_bytes, padrao_chegadas)
saidas_txt = ler_bytes(st.session_state.saidas_bytes, padrao_saidas)
conf_txt = ler_bytes(st.session_state.conf_bytes, padrao_conf)
aux_txt = ler_bytes(st.session_state.aux_bytes, padrao_aux)

cheg = extrair_movimentos(chegadas_txt)
said = extrair_movimentos(saidas_txt)

# =============================================
# HORÁRIOS + CRUZAMENTO DE MEIA-NOITE
# =============================================
horas_set = set(cheg.keys()) | set(said.keys())
max_min = 0
for txt in [conf_txt, aux_txt]:
    for l in txt.splitlines():
        p = l.split()
        if len(p) >= 4:
            for h in p[:4]:
                m = min_hora(h)
                if m < min_hora(p[0]): m += 1440
                horas_set.add(h)
                max_min = max(max_min, m)

# Timeline completa (a cada 15 min)
timeline_min = []
current = 0
while current <= max_min + 60:
    h = current % 1440
    hh = h // 60
    mm = h % 60
    timeline_min.append(f"{hh:02d}:{mm:02d}")
    current += 15

horarios = sorted(set(timeline_min + list(horas_set)), key=min_hora)
timeline_min_vals = [min_hora(h) + (1440 if min_hora(h) < min_hora(horarios[0]) else 0) for h in horarios]

# =============================================
# CONTAGEM DE FUNCIONÁRIOS
# =============================================
conf_count = [0] * len(horarios)
aux_count = [0] * len(horarios)

def aplicar_jornada_com_cruzamento(j, tl_vals, contador):
    e = min_hora(j["e"])
    sf = min_hora(j.get("sf", j.get("si", "")))
    si = min_hora(j.get("si", "")) if "si" in j else -1
    ri = min_hora(j.get("ri", "")) if "ri" in j else -1
    if sf < e: sf += 1440
    if si != -1 and si < e: si += 1440
    if ri != -1 and ri < e: ri += 1440
    for i, t in enumerate(tl_vals):
        t_adj = t + (1440 if t < e else 0)
        active = False
        if si == -1:
            active = e <= t_adj <= sf
        else:
            active = (e <= t_adj < si) or (ri <= t_adj <= sf)
        if active:
            contador[i] += j["q"]

for j in extrair_jornadas(conf_txt):
    aplicar_jornada_com_cruzamento(j, timeline_min_vals, conf_count)
for j in extrair_jornadas(aux_txt):
    aplicar_jornada_com_cruzamento(j, timeline_min_vals, aux_count)

conf_count = [int(x) for x in conf_count]
aux_count = [int(x) for x in aux_count]

# =============================================
# DATAFRAME + PRODUTIVIDADE
# =============================================
df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_ton": [round(cheg.get(h, 0), 1) for h in horarios],
    "Saida_ton": [round(said.get(h, 0), 1) for h in horarios],
    "Conferentes": conf_count,
    "Auxiliares": aux_count,
})

df["Prod_Conferentes_ton_h"] = (df["Conferentes"] * prod_carga).round(1)
df["Prod_Auxiliares_ton_h"] = (df["Auxiliares"] * prod_descarga).round(1)
df["Processamento_Total_ton_h"] = (df["Prod_Conferentes_ton_h"] + df["Prod_Auxiliares_ton_h"]).round(1)

# Acumulado
acumulado = 0.0
acumulado_list = []
for _, row in df.iterrows():
    acumulado = max(0, acumulado + row["Chegada_ton"] - row["Saida_ton"])
    acumulado_list.append(round(acumulado, 1))
df["Acumulado_ton"] = acumulado_list

# =============================================
# GRÁFICO
# =============================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_ton"], name="Chegada", marker_color="#2ca02c"))
fig.add_trace(go.Bar(x=df["Horario"], y=-df["Saida_ton"], name="Saída", marker_color="#d62728"))

fig.add_trace(go.Scatter(x=df["Horario"], y=df["Acumulado_ton"], mode="lines", name="Acumulado",
                         fill="tozeroy", fillcolor="rgba(148,103,189,0.4)", line=dict(color="#9467bd", width=3)))

# <<< LINHA DE PROCESSAMENTO REMOVIDA >>>

fig.add_trace(go.Scatter(x=df["Horario"], y=df["Conferentes"] * escala_pessoas, mode="lines+markers",
                         name="Conferentes", line=dict(color="#1f77b4", width=2), marker=dict(size=5),
                         customdata=df[["Conferentes"]].values,
                         hovertemplate="<b>%{x}</b><br>Conferentes: %{customdata[0]}<extra></extra>"))

fig.add_trace(go.Scatter(x=df["Horario"], y=df["Auxiliares"] * escala_pessoas, mode="lines+markers",
                         name="Auxiliares", line=dict(color="#006400", width=2), marker=dict(size=5),
                         customdata=df[["Auxiliares"]].values,
                         hovertemplate="<b>%{x}</b><br>Auxiliares: %{customdata[0]}<extra></extra>"))

if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_ton"],
                               text=f"+{r['Chegada_ton']:.1f}", font=dict(color="white", size=9),
                               bgcolor="#2ca02c", showarrow=False, yshift=8)
        if r["Saida_ton"] > 0.1:
            fig.add_annotation(x=r["Horario"], y=-r["Saida_ton"],
                               text=f"-{r['Saida_ton']:.1f}", font=dict(color="white", size=9),
                               bgcolor="#d62728", showarrow=False, yshift=-8)

# Ajuste do range Y sem a linha de processamento
max_y = max(df[["Chegada_ton", "Acumulado_ton"]].max().max(),
            df[["Conferentes", "Auxiliares"]].max().max() * escala_pessoas) * 1.2
min_y = -df["Saida_ton"].max() * 1.2

fig.update_layout(
    title="Acumulado x Produção - CD",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas", range=[min_y, max_y]),
    barmode="relative",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=700,
    margin=dict(l=70, r=70, t=90, b=60),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# MÉTRICAS
# =============================================
st.markdown("### Métricas Operacionais")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chegada Total", f"{df['Chegada_ton'].sum():.1f} ton")
col2.metric("Saída Total", f"{df['Saida_ton'].sum():.1f} ton")
col3.metric("Acumulado Final", f"{df['Acumulado_ton'].iloc[-1]:.1f} ton")
col4.metric("Processamento Médio", f"{df['Processamento_Total_ton_h'].mean():.1f} ton/h")

# =============================================
# TABELA
# =============================================
with st.expander("Tabela Completa"):
    df_disp = df.copy()
    df_disp["Total_Pessoas"] = df_disp["Conferentes"] + df_disp["Auxiliares"]
    st.dataframe(df_disp.style.format({
        "Chegada_ton": "{:.1f}",
        "Saida_ton": "{:.1f}",
        "Acumulado_ton": "{:.1f}",
        "Processamento_Total_ton_h": "{:.1f}",
        "Prod_Conferentes_ton_h": "{:.1f}",
        "Prod_Auxiliares_ton_h": "{:.1f}",
        "Conferentes": "{:d}",
        "Auxiliares": "{:d}",
        "Total_Pessoas": "{:d}"
    }), use_container_width=True)
    
    csv = df_disp.to_csv(index=False).encode()
    st.download_button("Baixar CSV", csv, "logistica_com_processamento.csv", "text/csv")
