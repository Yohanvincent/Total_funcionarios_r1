# pages/1_Conferentes_vs_Auxiliares.py (CACHE + COMENTÁRIOS + ZERO ERROS)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(layout="wide")  # Layout largo para melhor visualização

st.title("Disponibilidade: Conferentes vs Auxiliares")
st.markdown("**Upload (Excel/CSV/TXT) ou use padrão.**")

# =============================================
# CACHE DE UPLOAD: NÃO PERDE DADOS AO TROCAR DE ABA
# =============================================
# @st.cache_data mantém o arquivo carregado em memória
# Mesmo ao navegar entre páginas, o upload persiste
@st.cache_data(show_spinner=False)
def carregar_arquivo(uploaded_file):
    """Lê e retorna o conteúdo do arquivo como string com quebras de linha."""
    if uploaded_file is None:
        return None
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, header=None)
        return "\n".join(" ".join(map(str, row)) for row in df.values)
    else:
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

# Uploaders com chaves únicas
c1, c2 = st.columns(2)
with c1:
    up_conf = st.file_uploader("Conferentes", ["txt", "csv", "xlsx"], key="conf_upload")
with c2:
    up_aux = st.file_uploader("Auxiliares", ["txt", "csv", "xlsx"], key="aux_upload")

# Dados padrão (usados se não houver upload)
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

# Carrega com cache
jc = carregar_arquivo(up_conf) or padrao_conf
ja = carregar_arquivo(up_aux) or padrao_aux

# =============================================
# FUNÇÕES DE PROCESSAMENTO
# =============================================
def extrair_jornadas(texto):
    """Extrai jornadas do texto: completa (5 partes) ou meia (3 partes)."""
    jornadas = []
    for linha in texto.strip().split("\n"):
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():
            jornadas.append({"tipo": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            jornadas.append({"tipo": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return jornadas

def minutos(h):
    """Converte 'HH:MM' → minutos do dia."""
    try:
        h, m = map(int, h.split(":"))
        return h * 60 + m
    except:
        return 0

def coletar_horarios(jc, ja):
    """Coleta e ordena todos os horários únicos."""
    h = {"00:00", "23:59"}
    for t in [jc, ja]:
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if len(p) in (3, 5):
                h.update(p[:-1])
    return sorted(h, key=minutos)

# =============================================
# CÁLCULO DE DISPONIBILIDADE
# =============================================
horarios = coletar_horarios(jc, ja)
timeline = [minutos(h) for h in horarios]
conf_count = [0] * len(timeline)
aux_count = [0] * len(timeline)

def aplicar_jornada(j, lista, tl):
    """Aplica jornada na timeline."""
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
    aplicar_jornada(j, conf_count, timeline)
for j in extrair_jornadas(ja):
    aplicar_jornada(j, aux_count, timeline)

df = pd.DataFrame({"Horario": horarios, "Conferentes": conf_count, "Auxiliares": aux_count})

# =============================================
# CONTROLES E DOWNLOAD
# =============================================
c1, c2, _ = st.columns([1, 1, 6])
with c1:
    rotulos = st.checkbox("Rótulos", True)
with c2:
    st.markdown("**Clique no gráfico para maximizar**")

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
# GRÁFICO
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
                text=str(int(r["Conferentes"])),
                showarrow=False,
                font=dict(color="#90EE90", size=10, family="bold"),
                bgcolor="white", bordercolor="#90EE90", borderwidth=1, borderpad=4
            )
        if r["Auxiliares"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Auxiliares"] + 0.8,
                text=str(int(r["Auxiliares"])),
                showarrow=False,
                font=dict(color="#228B22", size=10, family="bold"),
                bgcolor="white", bordercolor="#228B22", borderwidth=1, borderpad=4
            )

fig.update_layout(
    title="Disponibilidade de Equipe",
    xaxis_title="Horário",
    yaxis_title="Pessoas",
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=80, b=40),
    legend=dict(x=0, y=1)
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# EXPLICAÇÃO DE UPLOAD
# =============================================
with st.expander("Como preparar os arquivos para upload"):
    st.markdown(
        "### Formato das linhas:\n\n"
        "| Tipo | Formato | Exemplo |\n"
        "|------|--------|--------|\n"
        "| Completa | `entrada saída_int retorno saída_final qtd` | `04:00 09:00 10:15 13:07 27` |\n"
        "| Meia | `entrada saída_final qtd` | `17:48 21:48 1` |\n\n"
        "### Regras:\n"
        "- `HH:MM` (24h)\n"
        "- Uma linha = um grupo\n"
        "- Quantidade = inteiro\n"
        "- Separado por espaços\n"
        "- Sem cabeçalho\n\n"
        "### Exemplo TXT:\n"
        "```\n00:00 04:00 05:15 09:33 9\n04:00 09:00 10:15 13:07 27\n```\n\n"
        "> Copie do Excel → Bloco de Notas → Salve como `.txt`"
    )

st.markdown("**Upload → Rótulos → Maximizar → Baixar**")
