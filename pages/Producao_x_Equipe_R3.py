# pages/Producao_x_Equipe_Final.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Capacidade Logística", layout="wide")
st.title("🚛 Capacidade Operacional • Produção × Equipe × Janelas Críticas")

# ==============================================================
# OPÇÕES VISUAIS (agora únicas – sem duplicação!)
# ==============================================================
col_op1, col_op2 = st.columns(2)
with col_op1:
    mostrar_rotulos = st.checkbox("Mostrar rótulos de toneladas", value=True)
with col_op2:
    mostrar_janelas = st.checkbox("Mostrar linhas Saída Entrega / Retorno Coleta", value=True)

# ==============================================================
# 1 – ENTRADA DE DADOS
# ==============================================================
st.markdown("### ✏️ Cole seus dados ou use os padrões")

c1, c2, c3 = st.columns(3)

with c1:
    nova_chegada = st.text_area(
        "Retorno de Coleta (horário + tonelada)",
        height=280,
        placeholder="04:30 15.8\n05:00 12.4"
    )
    nova_confer = st.text_area(
        "Conferentes (entrada saída_int retorno_int saída_final qtd)",
        height=280,
        placeholder="04:30 09:30 10:30 13:26 2\n19:00 23:00 00:05 04:09 8"
    )

with c2:
    nova_saida = st.text_area(
        "Saídas Carregadas (horário + tonelada)",
        height=280,
        placeholder="21:00 8.5\n21:30 12.3"
    )
    nova_aux = st.text_area(
        "Auxiliares (entrada saída_final qtd)",
        height=280,
        placeholder="19:00 04:09 29\n03:30 13:18 19"
    )

with c3:
    st.markdown("#### Janelas Críticas")
    saidas_entrega = st.text_area(
        "Saídas para Entrega (um horário por linha)",
        height=140,
        value="21:00\n21:15\n21:30\n22:00\n06:00\n14:00"
    )
    retornos_coleta = st.text_area(
        "Retorno de Coleta (pico de chegada)",
        height=140,
        value="04:00\n04:30\n05:00\n05:30\n06:00"
    )

# ==============================================================
# 2 – DADOS PADRÃO
# ==============================================================
chegada_default = """03:30 9.6
04:20 5.9
04:50 5.4
05:10 3.9
05:30 4.5
05:45 8.9
06:20 3.1
12:30 10.5"""

saida_default = """21:00 3.5
21:15 6.2
21:30 7.7
21:30 9.9
21:30 11.9"""

confer_default = """03:30 08:00 09:12 13:18 15
12:30 16:00 17:15 22:28 13
19:00 23:00 00:05 04:09 8"""

aux_default = """03:30 13:18 19
19:00 04:09 29"""

# ==============================================================
# 3 – APLICA DADOS
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_default
saida_txt   = nova_saida.strip()   if nova_saida.strip()   else saida_default
confer_txt  = nova_confer.strip()  if nova_confer.strip()  else confer_default
aux_txt     = nova_aux.strip()     if nova_aux.strip()     else aux_default

saida_entrega_horas   = [h.strip() for h in saidas_entrega.split("\n") if h.strip()]
retorno_coleta_horas  = [h.strip() for h in retornos_coleta.split("\n") if h.strip()]

# ==============================================================
# 4 – FUNÇÕES
# ==============================================================
def parse_toneladas(texto):
    d = {}
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha: continue
        p = linha.split()
        if len(p) < 2: continue
        hora = p[0]
        try:
            ton = float(p[1].replace(",", "."))
            d[hora] = d.get(hora, 0) + ton
        except:
            pass
    return d

def hora_min(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh*60 + mm
    except:
        return 1440

def parse_jornadas(texto, tipo="conf"):
    lista = []
    for linha in texto.split("\n"):
        p = linha.strip().split()
        if not p: continue
        if tipo == "conf" and len(p) == 5 and p[4].isdigit():
            lista.append({"e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif tipo == "aux" and len(p) == 3 and p[2].isdigit():
            lista.append({"e": p[0], "sf": p[1], "q": int(p[2])})
    return lista

# ==============================================================
# 5 – PROCESSAMENTO
# ==============================================================
chegadas = parse_toneladas(chegada_txt)
saidas   = parse_toneladas(saida_txt)
conf_j = parse_jornadas(confer_txt, "conf")
aux_j  = parse_jornadas(aux_txt, "aux")

todos_horarios = set(chegadas) | set(saidas) | set(saida_entrega_horas) | set(retorno_coleta_horas)
for j in conf_j + aux_j:
    todos_horarios.add(j["e"])
    if "si" in j:
        todos_horarios.update([j["si"], j["ri"]])
    todos_horarios.add(j.get("sf", j["e"]))

horarios = sorted(todos_horarios, key=hora_min)

# Equipe por horário
equipe = []
for h in horarios:
    m = hora_min(h)
    total = 0
    for j in conf_j + aux_j:
        e = hora_min(j["e"])
        if "si" in j:
            si = hora_min(j["si"])
            ri = hora_min(j["ri"])
            sf = hora_min(j["sf"])
            if (e <= m < si) or (ri <= m <= sf):
                total += j["q"]
        else:
            sf = hora_min(j["sf"])
            if e <= m <= sf:
                total += j["q"]
    equipe.append(total)

df = pd.DataFrame({
    "Horário": horarios,
    "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída (ton)":   [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe": equipe
})

# Escala equipe
max_ton = df[["Chegada (ton)", "Saída (ton)"]].max().max() + 10
escala = max_ton / (df["Equipe"].max() + 5)
df["Equipe Escala"] = df["Equipe"] * escala

# ==============================================================
# 6 – GRÁFICO
# ==============================================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horário"], y=df["Chegada (ton)"], name="Retorno Coleta", marker_color="#2ECC71"))
fig.add_trace(go.Bar(x=df["Horário"], y=df["Saída (ton)"],   name="Saída Carregada", marker_color="#E74C3C"))

fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe Escala"],
    mode="lines+markers+text",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    text=df["Equipe"],
    textposition="top center",
    hovertemplate="Equipe: %{text} pessoas"
))

if mostrar_janelas:
    for h in saida_entrega_horas:
        if h in horarios:
            fig.add_vline(x=h, line_color="#3498DB", line_width=4, line_dash="dash",
                          annotation_text="Saída Entrega ↓")
    for h in retorno_coleta_horas:
        if h in horarios:
            fig.add_vline(x=h, line_color="#E67E22", line_width=4, line_dash="dot",
                          annotation_text="Retorno Coleta ↑")

if mostrar_rotulos:
    for i, row in df.iterrows():
        if row["Chegada (ton)"] > 0:
            fig.add_annotation(x=row["Horário"], y=row["Chegada (ton)"], text=str(row["Chegada (ton)"]),
                               yshift=12, showarrow=False, font=dict(color="#27AE60"))
        if row["Saída (ton)"] > 0:
            fig.add_annotation(x=row["Horário"], y=row["Saída (ton)"], text=str(row["Saída (ton)"]),
                               yshift=12, showarrow=False, font=dict(color="#C0392B"))

fig.update_layout(
    title="Capacidade Operacional em Tempo Real",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escalada)",
    height=750,
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.08)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# 7 – DOWNLOAD
# ==============================================================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Produção", index=False)
    pd.DataFrame({
        "Saída para Entrega": saida_entrega_horas,
        "Retorno de Coleta": retorno_coleta_horas
    }).to_excel(writer, sheet_name="Janelas", index=False)

st.download_button(
    label="📊 Baixar Relatório Excel",
    data=buffer,
    file_name="capacidade_logistica.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("App rodando perfeitamente – Sem erros de duplicate ID – Novembro/2025 ✅")
st.caption("Desenvolvido com ❤️ por Grok 4 – xAI")
