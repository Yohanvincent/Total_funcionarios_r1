# pages/1_Conferentes_vs_Auxiliares.py (CACHE DE UPLOAD + COMENTÁRIOS + DOCUMENTAÇÃO)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(layout="wide")  # Usa toda a largura da tela

st.title("Disponibilidade: Conferentes vs Auxiliares")
st.markdown("**Upload (Excel/CSV/TXT) ou use padrão.**")

# =============================================
# UPLOAD DE ARQUIVOS COM CACHE (NÃO PERDE AO TROCAR DE ABA)
# =============================================
# @st.cache_data permite que o arquivo lido seja mantido mesmo ao navegar entre páginas
@st.cache_data(show_spinner=False)
def carregar_arquivo(uploaded_file):
    """Lê arquivo TXT, CSV ou Excel e retorna como string com quebras de linha."""
    if uploaded_file is None:
        return None
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, header=None)
        return "\n".join(" ".join(map(str, row)) for row in df.values)
    else:
        return uploaded_file.getvalue().decode("utf-8")

# Colunas para upload
c1, c2 = st.columns(2)
with c1:
    up_conf = st.file_uploader("Conferentes", ["txt", "csv", "xlsx"], key="conf_uploader")
with c2:
    up_aux = st.file_uploader("Auxiliares", ["txt", "csv", "xlsx"], key="aux_uploader")

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

# Carrega arquivos com cache
jc = carregar_arquivo(up_conf) or padrao_conf
ja = carregar_arquivo(up_aux) or padrao_aux

# =============================================
# PROCESSAMENTO DE JORNADAS
# =============================================
def extrair_jornadas(texto):
    """Converte texto em lista de jornadas (completa ou meia)."""
    jornadas = []
    for linha in texto.strip().split("\n"):
        partes = linha.strip().split()
        if len(partes) == 5 and partes[4].isdigit():
            # Jornada completa: entrada, saída_intervalo, retorno, saída_final, qtd
            jornadas.append({
                "tipo": "c",
                "e": partes[0],
                "si": partes[1],
                "ri": partes[2],
                "sf": partes[3],
                "q": int(partes[4])
            })
        elif len(partes) == 3 and partes[2].isdigit():
            # Jornada meia: entrada, saída_final, qtd
            jornadas.append({
                "tipo": "m",
                "e": partes[0],
                "sf": partes[1],
                "q": int(partes[2])
            })
    return jornadas

def minutos(horario):
    """Converte 'HH:MM' em minutos do dia (0 a 1439)."""
    try:
        h, m = map(int, horario.split(":"))
        return h * 60 + m
    except:
        return 0

def coletar_horarios(jc, ja):
    """Coleta todos os horários únicos de entrada/saída e ordena."""
    horarios = {"00:00", "23:59"}
    for texto in [jc, ja]:
        for linha in texto.strip().split("\n"):
            partes = linha.strip().split()
            if len(partes) in (3, 5):
                horarios.update(partes[:-1])
    return sorted(horarios, key=minutos)

# =============================================
# CÁLCULO DE DISPONIBILIDADE
# =============================================
horarios_lista = coletar_horarios(jc, ja)
timeline_min = [minutos(h) for h in horarios_lista]
conferentes = [0] * len(timeline_min)
auxiliares = [0] * len(timeline_min)

def aplicar_jornada(jornada, lista, timeline):
    """Adiciona quantidade de pessoas na timeline conforme jornada."""
    entrada = minutos(jornada["e"])
    saida_final = minutos(jornada["sf"])
    if jornada["tipo"] == "c":
        saida_int = minutos(jornada["si"])
        retorno = minutos(jornada["ri"])
        for i, t in enumerate(timeline):
            if (entrada <= t < saida_int) or (retorno <= t <= saida_final):
                lista[i] += jornada["q"]
    else:
        for i, t in enumerate(timeline):
            if entrada <= t <= saida_final:
                lista[i] += jornada["q"]

# Processa todas as jornadas
for j in extrair_jornadas(jc):
    aplicar_jornada(j, conferentes, timeline_min)
for j in extrair_jornadas(ja):
    aplicar_jornada(j, auxiliares, timeline_min)

# =============================================
# DATAFRAME FINAL
# =============================================
df = pd.DataFrame({
    "Horario": horarios_lista,
    "Conferentes": conferentes,
    "Auxiliares": auxiliares
})

# =============================================
# CONTROLES E DOWNLOAD
# =============================================
c1, c2, _ = st.columns([1, 1, 6])
with c1:
    mostrar_rotulos = st.checkbox("Rótulos", True)
with c2:
    st.markdown("**Clique no gráfico para maximizar**")

# Download do resultado
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
output.seek(0)

st.download_button(
    label="📥 Baixar Excel",
    data=output,
    file_name="equipe.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================
# GRÁFICO INTERATIVO
# =============================================
fig = go.Figure()

# Trace: Conferentes
fig.add_trace(go.Scatter(
    x=df["Horario"],
    y=df["Conferentes"],
    mode="lines+markers",
    name="Conferentes",
    line=dict(color="#90EE90", width=4),
    marker=dict(size=6),
    fill="tozeroy",
    fillcolor="rgba(144, 238, 144, 0.3)"
))

# Trace: Auxiliares
fig.add_trace(go.Scatter(
    x=df["Horario"],
    y=df["Auxiliares"],
    mode="lines+markers",
    name="Auxiliares",
    line=dict(color="#228B22", width=4),
    marker=dict(size=6),
    fill="tozeroy",
    fillcolor="rgba(34, 139, 34, 0.3)"
))

# Intervalo de almoço (se existir)
if "09:30" in df["Horario"].values and "10:30" in df["Horario"].values:
    fig.add_vrect(x0="09:30", x1="10:30", fillcolor="gray", opacity=0.1, line_width=0)

# Rótulos com caixinha (apenas se ativado)
if mostrar_rotulos:
    for _, row in df.iterrows():
        if row["Conferentes"] > 0:
            fig.add_annotation(
                x=row["Horario"],
                y=row["Conferentes"] + 0.8,
                text=str(int(row["Conferentes"])),
                showarrow=False,
                font=dict(color="#90EE90", size=10, family="bold"),
                bgcolor="white",
                bordercolor="#90EE90",
                borderwidth=1,
                borderpad=4
            )
        if row["Auxiliares"] > 0:
            fig.add_annotation(
                x=row["Horario"],
                y=row["Auxiliares"] + 0.8,
                text=str(int(row["Auxiliares"])),
                showarrow=False,
                font=dict(color="#228B22", size=10, family="bold"),
                bgcolor="white",
                bordercolor="#228B22",
                borderwidth=1,
                borderpad=4
            )

# Layout do gráfico
fig.update_layout(
    title="Disponibilidade de Equipe",
    xaxis_title="Horário",
    yaxis_title="Pessoas",
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=80, b=40),
    legend=dict(x=0, y=1, bgcolor="rgba(255,255,255,0.8)", bordercolor="gray", borderwidth=1)
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# EXPLICAÇÃO DE UPLOAD (EXPANDÍVEL)
# =============================================
with st.expander("📋 Como preparar os arquivos para upload", expanded=False):
    st.markdown("""
### Formato das linhas (separadas por espaço):

| Tipo | Formato | Exemplo |
|------|--------|--------|
| **Jornada Completa** | `entrada saída_intervalo retorno_intervalo saída_final qtd` | `04:00 09:00 10:15 13:07 27` |
| **Jornada Meia** | `entrada saída_final qtd` | `17:48 21:48 1` |

### Regras:
- Horários em `HH:MM` (24h)
- Uma linha = um grupo com mesma jornada
- Quantidade = número inteiro
- Separado por **espaços**
- **Sem cabeçalho**

### Exemplo TXT:
