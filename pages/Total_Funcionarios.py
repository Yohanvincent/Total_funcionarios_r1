# pages/2_Total_Funcionarios.py
# =============================================
# OBJETIVO: Somar Conferentes + Auxiliares e exibir total por horário
# FUNCIONALIDADES:
#   • Upload persistente entre abas (session_state)
#   • Visualização do nome e conteúdo dos arquivos
#   • Gráfico com total de funcionários
#   • Rótulos em negrito com caixinha branca
#   • Download do resultado em Excel
# =============================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# 1. CONFIGURAÇÃO INICIAL DA PÁGINA
# =============================================
st.set_page_config(layout="wide")                    # Usa toda a largura da tela
st.title("Disponibilidade Total de Funcionários")
st.markdown("**Upload (Excel/CSV/TXT) ou use padrão.**")

# =============================================
# 2. PERSISTÊNCIA DE UPLOAD COM session_state
#    → Garante que os arquivos não sumam ao trocar de aba
# =============================================
# Inicializa variáveis no estado da sessão
if "total_conf_bytes" not in st.session_state:
    st.session_state.total_conf_bytes = None         # Bytes do arquivo Conferentes
if "total_aux_bytes" not in st.session_state:
    st.session_state.total_aux_bytes = None          # Bytes do arquivo Auxiliares
if "total_conf_name" not in st.session_state:
    st.session_state.total_conf_name = None          # Nome do arquivo Conferentes
if "total_aux_name" not in st.session_state:
    st.session_state.total_aux_name = None           # Nome do arquivo Auxiliares

# =============================================
# 3. UPLOADERS COM FEEDBACK VISUAL
# =============================================
c1, c2 = st.columns(2)

with c1:
    # Upload para Conferentes
    up_conf = st.file_uploader(
        "Conferentes",
        ["txt", "csv", "xlsx"],
        key="total_conf_uploader",
        help="Upload persiste entre abas"
    )
    if up_conf is not None:
        # Salva bytes e nome no session_state
        st.session_state.total_conf_bytes = up_conf.getvalue()
        st.session_state.total_conf_name = up_conf.name
    # Exibe confirmação com nome do arquivo
    if st.session_state.total_conf_name:
        st.success(f"Conferentes: **{st.session_state.total_conf_name}**")

with c2:
    # Upload para Auxiliares
    up_aux = st.file_uploader(
        "Auxiliares",
        ["txt", "csv", "xlsx"],
        key="total_aux_uploader"
    )
    if up_aux is not None:
        st.session_state.total_aux_bytes = up_aux.getvalue()
        st.session_state.total_aux_name = up_aux.name
    if st.session_state.total_aux_name:
        st.success(f"Auxiliares: **{st.session_state.total_aux_name}**")

# =============================================
# 4. DADOS PADRÃO (caso não haja upload)
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
# 5. FUNÇÃO: LER ARQUIVO (TXT ou Excel)
# =============================================
def ler_bytes(bytes_data, fallback):
    """Converte bytes em string com quebras de linha. Suporta TXT, CSV e Excel."""
    if bytes_data is None:
        return fallback
    try:
        return bytes_data.decode("utf-8")            # Tenta como texto puro
    except:
        # Fallback para Excel
        df = pd.read_excel(io.BytesIO(bytes_data), header=None)
        return "\n".join(" ".join(map(str, row)) for row in df.values)

# Aplica leitura com fallback
jc = ler_bytes(st.session_state.total_conf_bytes, padrao_conf)
ja = ler_bytes(st.session_state.total_aux_bytes, padrao_aux)

# =============================================
# 6. FUNÇÕES DE PROCESSAMENTO DE JORNADAS
# =============================================
def extrair_jornadas(texto):
    """Extrai jornadas do texto. Suporta completa (5 colunas) e meia (3 colunas)."""
    jornadas = []
    for linha in texto.strip().split("\n"):
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():
            # Jornada completa: entrada, saída_int, retorno, saída_final, qtd
            jornadas.append({"tipo": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            # Jornada meia: entrada, saída_final, qtd
            jornadas.append({"tipo": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return jornadas

def minutos(h):
    """Converte 'HH:MM' em minutos do dia (0 a 1439)."""
    try:
        h, m = map(int, h.split(":"))
        return h * 60 + m
    except:
        return 0

def coletar_horarios(jc, ja):
    """Coleta todos os horários únicos e ordena cronologicamente."""
    h = {"00:00", "23:59"}  # Garante início e fim do dia
    for t in [jc, ja]:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3, 5):
                h.update(p[:-1])
    return sorted(h, key=minutos)

# =============================================
# 7. CÁLCULO DO TOTAL POR HORÁRIO
# =============================================
horarios = coletar_horarios(jc, ja)                   # Lista de horários únicos
timeline = [minutos(h) for h in horarios]             # Timeline em minutos
total = [0] * len(timeline)                           # Total de funcionários

def aplicar_jornada(j, lista, tl):
    """Adiciona quantidade de pessoas na timeline conforme jornada."""
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

# Aplica jornadas de Conferentes + Auxiliares
for j in extrair_jornadas(jc):
    aplicar_jornada(j, total, timeline)
for j in extrair_jornadas(ja):
    aplicar_jornada(j, total, timeline)

# DataFrame final
df = pd.DataFrame({"Horario": horarios, "Total": total})

# =============================================
# 8. CONTROLES E DOWNLOAD
# =============================================
c1, c2, _ = st.columns([1, 1, 6])
with c1:
    rotulos = st.checkbox("Rótulos", True)           # Liga/desliga rótulos  

# Exporta para Excel
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
output.seek(0)

st.download_button(
    "Baixar Excel",
    output,
    "total.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================
# 9. GRÁFICO INTERATIVO
# =============================================
fig = go.Figure()

# Linha do total de funcionários
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Total"],
    mode="lines+markers", name="Total",
    line=dict(color="#90EE90", width=4), marker=dict(size=6),
    fill="tozeroy", fillcolor="rgba(144, 238, 144, 0.3)"
))

# Intervalo de almoço (se aplicável)
if "09:30" in df["Horario"].values and "10:30" in df["Horario"].values:
    fig.add_vrect(x0="09:30", x1="10:30", fillcolor="gray", opacity=0.1)

# Rótulos com negrito e caixinha
if rotulos:
    for _, r in df.iterrows():
        if r["Total"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Total"] + 0.8,
                text=f"<b>{int(r['Total'])}</b>",        # NEGRITO FORÇADO
                showarrow=False,
                font=dict(color="#90EE90", size=10),
                bgcolor="white", bordercolor="#90EE90", borderwidth=1, borderpad=4
            )

# Layout final do gráfico
fig.update_layout(
    title="Total de Funcionários",
    xaxis_title="Horário",
    yaxis_title="Total",
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=80, b=40)
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# 10. VISUALIZAÇÃO DOS DADOS CARREGADOS
# =============================================
if st.session_state.total_conf_name or st.session_state.total_aux_name:
    st.markdown("### Dados carregados (visualização)")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.total_conf_name:
            st.markdown(f"**Conferentes: {st.session_state.total_conf_name}**")
            st.code(jc, language="text")
    with col2:
        if st.session_state.total_aux_name:
            st.markdown(f"**Auxiliares: {st.session_state.total_aux_name}**")
            st.code(ja, language="text")

# =============================================
# 11. EXPLICAÇÃO DE COMO PREPARAR OS ARQUIVOS
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
