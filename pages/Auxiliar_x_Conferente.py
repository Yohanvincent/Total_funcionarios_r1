# pages/1_Conferentes_vs_Auxiliares.py
# =============================================
# OBJETIVO: Comparar disponibilidade de Conferentes vs Auxiliares
# LAYOUT:
#   1. Título
#   2. Checkbox de rótulos
#   3. Gráfico (logo abaixo do título)
#   4. Uploads (Conferentes + Auxiliares)
#   5. Botão Baixar Excel
#   6. Dados carregados (visualização)
#   7. Explicação de formato
# =============================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(layout="wide")

# =============================================
# 2. TÍTULO + CHECKBOX + GRÁFICO (NO INÍCIO)
# =============================================
st.title("👷Disponibilidade: Auxiliares Carga/Descarga x Conferentes")

# Checkbox de rótulos (logo abaixo do título)
rotulos = st.checkbox("Rótulos", True)

# =============================================
# 3. PERSISTÊNCIA DE UPLOAD (session_state)
# =============================================
if "conf_bytes" not in st.session_state:
    st.session_state.conf_bytes = None
if "aux_bytes" not in st.session_state:
    st.session_state.aux_bytes = None
if "conf_name" not in st.session_state:
    st.session_state.conf_name = None
if "aux_name" not in st.session_state:
    st.session_state.aux_name = None

# =============================================
# 4. DADOS PADRÃO
# =============================================
padrao_conf = (
    "00:00 04:00 05:15 09:33 9\n04:00 09:00 10:15 13:07 27\n04:30 08:30 10:30 15:14 1\n"
    "06:00 11:00 12:15 16:03 1\n07:45 12:00 13:15 17:48 1\n08:00 12:00 13:15 18:03 2\n"
    "10:00 12:00 14:00 20:48 11\n12:00 16:00 17:15 22:02 8\n13:00 16:00 17:15 22:55 5\n"
    "15:45 18:00 18:15 22:00 7\n16:30 19:30 19:45 22:39 2"
)

padrao_aux = (
    "00:00 04:00 05:15 09:33 10\n04:00 09:00 10:15 13:07 17\n12:00 16:00 17:15 22:02 2\n"
    "13:00 16:00 17:15 22:55 3\n15:45 18:00 18:15 22:00 3\n16:30 19:30 19:45 22:39 2\n"
    "17:48 21:48 1\n18:00 22:00 19\n19:00 22:52 5"
)

# =============================================
# 5. FUNÇÃO: LER ARQUIVO
# =============================================
def ler_bytes(bytes_data, fallback):
    if bytes_data is None:
        return fallback
    try:
        return bytes_data.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(bytes_data), header=None)
        return "\n".join(" ".join(map(str, row)) for row in df.values)

# =============================================
# 6. PROCESSAMENTO (executado antes do gráfico)
# =============================================
jc = ler_bytes(st.session_state.conf_bytes, padrao_conf)
ja = ler_bytes(st.session_state.aux_bytes, padrao_aux)

def extrair_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():
            jornadas.append({"tipo": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            jornadas.append({"tipo": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return jornadas

def minutos(h):
    try:
        h, m = map(int, h.split(":"))
        return h * 60 + m
    except:
        return 0

def coletar_horarios(jc, ja):
    h = {"00:00", "23:59"}
    for t in [jc, ja]:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3, 5):
                h.update(p[:-1])
    return sorted(h, key=minutos)

horarios = coletar_horarios(jc, ja)
timeline = [minutos(h) for h in horarios]
conf = [0] * len(timeline)
aux = [0] * len(timeline)

def aplicar_jornada(j, lista, tl):
    e = minutos(j["e"])
    sf = minutos(j["sf"])
    if j["tipo"] == "c":
        si = minutos(j["si"])
        ri = minutos(j["ri"])
        for i, t in enumerate(tl):
            if (e <= t < si) or (ri <= t <= sf):
                lista[i] += j["q"]
    else:
        for i, t in enumerate(tl):
            if e <= t <= sf:
                lista[i] += j["q"]

for j in extrair_jornadas(jc):
    aplicar_jornada(j, conf, timeline)
for j in extrair_jornadas(ja):
    aplicar_jornada(j, aux, timeline)

df = pd.DataFrame({"Horario": horarios, "Conferentes": conf, "Auxiliares": aux})

# =============================================
# 7. GRÁFICO (logo após checkbox)
# =============================================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Conferentes"],
    mode="lines+markers", name="Conferentes",
    line=dict(color="#90EE90", width=4), marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(144, 238, 144, 0.3)"
))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Auxiliares"],
    mode="lines+markers", name="Auxiliares",
    line=dict(color="#228B22", width=4), marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(34, 139, 34, 0.3)"
))

if "09:30" in df["Horario"].values and "10:30" in df["Horario"].values:
    fig.add_vrect(x0="09:30", x1="10:30", fillcolor="gray", opacity=0.1)

if rotulos:
    for _, r in df.iterrows():
        if r["Conferentes"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Conferentes"] + 0.8,
                text=f"<b>{int(r['Conferentes'])}</b>",
                showarrow=False,
                font=dict(color="#90EE90", size=10),
                bgcolor="white", bordercolor="#90EE90", borderwidth=1, borderpad=4
            )
        if r["Auxiliares"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Auxiliares"] + 0.8,
                text=f"<b>{int(r['Auxiliares'])}</b>",
                showarrow=False,
                font=dict(color="#228B22", size=10),
                bgcolor="white", bordercolor="#228B22", borderwidth=1, borderpad=4
            )

fig.update_layout(
    title="",
    xaxis_title="Horário",
    yaxis_title="Pessoas",
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=20, b=40),
    legend=dict(x=0, y=1)
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# 8. UPLOADS (ABAIXO DO GRÁFICO)
# =============================================
st.markdown("**Upload (Excel/CSV/TXT) ou use padrão.**")

c1, c2 = st.columns(2)

with c1:
    up_conf = st.file_uploader(
        "Conferentes",
        ["txt", "csv", "xlsx"],
        key="conf_uploader",
        help="Upload persiste entre abas"
    )
    if up_conf is not None:
        st.session_state.conf_bytes = up_conf.getvalue()
        st.session_state.conf_name = up_conf.name
    if st.session_state.conf_name:
        st.success(f"Conferentes: **{st.session_state.conf_name}**")

with c2:
    up_aux = st.file_uploader(
        "Auxiliares",
        ["txt", "csv", "xlsx"],
        key="aux_uploader"
    )
    if up_aux is not None:
        st.session_state.aux_bytes = up_aux.getvalue()
        st.session_state.aux_name = up_aux.name
    if st.session_state.aux_name:
        st.success(f"Auxiliares: **{st.session_state.aux_name}**")

# =============================================
# 9. BOTÃO BAIXAR EXCEL
# =============================================
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
output.seek(0)

st.download_button(
    "Baixar Excel",
    output,
    "equipe.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================
# 10. VISUALIZAÇÃO DOS DADOS CARREGADOS
# =============================================
if st.session_state.conf_name or st.session_state.aux_name:
    st.markdown("### Dados carregados (visualização)")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.conf_name:
            st.markdown(f"**Conferentes: {st.session_state.conf_name}**")
            st.code(jc, language="text")
    with col2:
        if st.session_state.aux_name:
            st.markdown(f"**Auxiliares: {st.session_state.aux_name}**")
            st.code(ja, language="text")

# =============================================
# 11. EXPLICAÇÃO DE FORMATO
# =============================================
with st.expander("Como preparar os arquivos"):
    st.markdown(
        "### Formato das linhas:\n\n"
        "| Tipo       | Exemplo                     |\n"
        "|------------|-----------------------------|\n"
        "| Completa   | `04:00 09:00 10:15 13:07 27` |\n"
        "| Meia       | `17:48 21:48 1`             |\n\n"
        "- Horário: `HH:MM` (24h)\n"
        "- Uma linha = um grupo com mesma jornada\n"
        "- Quantidade no final (inteiro)\n"
        "- Separado por **espaços**\n"
        "- **Sem cabeçalho**\n\n"
        "> **Dica:** Copie do Excel → Bloco de Notas → Salve como `.txt`"
    )
