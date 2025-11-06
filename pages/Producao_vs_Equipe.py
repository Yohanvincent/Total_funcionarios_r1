# pages/3_Producao_vs_Equipe.py
# =============================================
# OBJETIVO: Comparar Produção (toneladas) vs Equipe Disponível
# LAYOUT:
#   1. Título
#   2. Checkbox de rótulos
#   3. Gráfico (colunas para produção + linha para equipe)
#   4. Upload de dados de produção (Cheg. + Saída)
#   5. Botão Baixar Excel
#   6. Dados carregados (visualização)
#   7. Explicação de formato
# =============================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta

# =============================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(layout="wide")

# =============================================
# 2. TÍTULO + CHECKBOX + GRÁFICO (NO INÍCIO)
# =============================================
st.title("Produção vs. Equipe Disponível")

rotulos = st.checkbox("Rótulos", True)

# =============================================
# 3. PERSISTÊNCIA DE UPLOAD (session_state)
# =============================================
if "prod_bytes" not in st.session_state:
    st.session_state.prod_bytes = None
if "prod_name" not in st.session_state:
    st.session_state.prod_name = None

# =============================================
# 4. DADOS PADRÃO DE PRODUÇÃO (Cheg. + Saída)
# =============================================
padrao_producao = (
    "Cheg. Ton.\n"
    "01:00 7,278041\n02:30 6,936955\n03:30 0\n04:00 3,542897\n04:30 1,676141\n"
    "05:15 14,263712\n05:30 4,482417\n05:50 3,695104\n06:00 4,389653\n06:00 3,4539\n"
    "06:00 2,153276\n06:00 2,852677\n06:30 2,720908\n07:15 6,567569\n07:30 1,44941\n"
    "09:30 12,076731\n10:15 0,1992\n11:00 1,462557\n12:45 0\n18:00 6,98727\n"
    "21:30 2,837159\n23:30 7,998834\n"
    "Saída Ton.\n"
    "03:15 5,618428\n04:45 0\n20:15 8,43512\n21:00 0,909347\n21:00 6,061068\n"
    "21:00 3,913779\n21:00 4,649687\n21:00 2,756661\n21:00 2,461966\n21:00 1,787873\n"
    "21:00 4,040584\n21:00 2,996577\n21:00 4,22898\n21:10 5,479109\n21:20 9,849377\n"
    "21:30 5,961456\n21:30 8,997052\n22:00 0,351623\n22:00 0,366688\n22:00 7,782288\n"
    "22:15 5,598385\n23:45 18,571689"
)

# =============================================
# 5. FUNÇÃO: LER ARQUIVO DE PRODUÇÃO
# =============================================
def ler_producao(bytes_data, fallback):
    if bytes_data is None:
        return fallback
    try:
        return bytes_data.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(bytes_data), header=None)
        return "\n".join(" ".join(map(str, row)) for row in df.values)

producao_texto = ler_producao(st.session_state.prod_bytes, padrao_producao)

# =============================================
# 6. PROCESSAMENTO: DADOS DE PRODUÇÃO (Chegada e Saída)
# =============================================
def extrair_producao(texto):
    chegadas = {}
    saidas = {}
    modo = None
    for linha in texto.strip().split("\n"):
        linha = linha.strip()
        if linha == "Cheg. Ton.":
            modo = "chegada"
            continue
        elif linha == "Saída Ton.":
            modo = "saida"
            continue
        if not linha or modo is None:
            continue
        partes = linha.split()
        if len(partes) >= 2:
            hora = partes[0]
            try:
                valor = float(partes[1].replace(",", "."))
                if modo == "chegada":
                    chegadas[hora] = chegadas.get(hora, 0) + valor
                else:
                    saidas[hora] = saidas.get(hora, 0) + valor
            except:
                continue
    return chegadas, saidas

chegadas, saidas = extrair_producao(producao_texto)

# =============================================
# 7. REUTILIZAÇÃO DA EQUIPE (TOTAL FUNCIONÁRIOS)
#    → Usa os mesmos cálculos da aba Total_Funcionarios
# =============================================
# --- DADOS PADRÃO DA EQUIPE (mesmos da outra aba) ---
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

horarios = coletar_horarios(padrao_conf, padrao_aux)
timeline = [minutos(h) for h in horarios]
total = [0] * len(timeline)

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

for j in extrair_jornadas(padrao_conf):
    aplicar_jornada(j, total, timeline)
for j in extrair_jornadas(padrao_aux):
    aplicar_jornada(j, total, timeline)

# =============================================
# 8. COMBINAR PRODUÇÃO COM HORÁRIOS DA EQUIPE
# =============================================
producao_por_hora = {h: 0.0 for h in horarios}
for hora, ton in chegadas.items():
    if hora in producao_por_hora:
        producao_por_hora[hora] += ton

df = pd.DataFrame({
    "Horario": horarios,
    "Equipe": total,
    "Producao_Ton": [producao_por_hora[h] for h in horarios]
})

# =============================================
# 9. GRÁFICO: COLUNAS (Produção) + LINHA (Equipe)
# =============================================
fig = go.Figure()

# Colunas: Produção (toneladas)
fig.add_trace(go.Bar(
    x=df["Horario"],
    y=df["Producao_Ton"],
    name="Produção (ton)",
    marker_color="#FF6B6B",
    yaxis="y",
    opacity=0.7
))

# Linha: Equipe disponível
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe"],
    mode="lines+markers", name="Equipe",
    line=dict(color="#4ECDC4", width=4),
    marker=dict(size=6),
    yaxis="y2"
))

# Rótulos
if rotulos:
    for _, r in df.iterrows():
        if r["Producao_Ton"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Producao_Ton"],
                text=f"<b>{r['Producao_Ton']:.1f}</b>",
                showarrow=False,
                font=dict(color="#FF6B6B", size=9),
                yshift=10
            )
        if r["Equipe"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Equipe"],
                text=f"<b>{int(r['Equipe'])}</b>",
                showarrow=False,
                font=dict(color="#4ECDC4", size=9),
                yshift=10
            )

fig.update_layout(
    title="",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas", side="left", showgrid=False),
    yaxis2=dict(title="Equipe", side="right", overlaying="y", showgrid=False),
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=60, t=20, b=40),
    legend=dict(x=0, y=1.1, orientation="h"),
    barmode="relative"
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# 10. UPLOAD DE PRODUÇÃO (ABAIXO DO GRÁFICO)
# =============================================
st.markdown("**Upload de Produção (Cheg. + Saída Ton.) ou use padrão.**")

up_prod = st.file_uploader(
    "Arquivo de Produção (TXT/CSV/XLSX)",
    ["txt", "csv", "xlsx"],
    key="prod_uploader",
    help="Formato: 'Cheg. Ton.' → HH:MM valor | 'Saída Ton.' → HH:MM valor"
)

if up_prod is not None:
    st.session_state.prod_bytes = up_prod.getvalue()
    st.session_state.prod_name = up_prod.name

if st.session_state.prod_name:
    st.success(f"Produção: **{st.session_state.prod_name}**")

# =============================================
# 11. BOTÃO BAIXAR EXCEL
# =============================================
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
output.seek(0)

st.download_button(
    "Baixar Excel",
    output,
    "producao_vs_equipe.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================
# 12. VISUALIZAÇÃO DOS DADOS CARREGADOS
# =============================================
if st.session_state.prod_name:
    st.markdown("### Dados de Produção Carregados")
    st.code(producao_texto, language="text")

# =============================================
# 13. EXPLICAÇÃO DE FORMATO
# =============================================
with st.expander("Como preparar o arquivo de produção"):
    st.markdown(
        """
        ### Formato esperado:
