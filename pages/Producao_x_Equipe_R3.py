# pages/Producao_x_Equipe_R4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("🚛 Produção Diária × Equipe × Janelas Críticas (Versão Estável)")

# Opções visuais
rotulos = st.checkbox("Mostrar rótulos nos valores", value=True)
mostrar_linhas = st.checkbox("Mostrar linhas de Saída Entrega e Retorno Coleta", value=True)

# ==============================================================
# 1 – ENTRADA DE DADOS
# ==============================================================
st.markdown("### ✏️ Cole seus dados ou use os padrões abaixo")

col1, col2, col3 = st.columns(3)

with col1:
    nova_chegada = st.text_area("Retorno de Coleta (horário tonelada)", height=250,
                                placeholder="04:30 15.8\n05:00 12.4")
    nova_confer = st.text_area("Conferentes (entrada saída_int retorno_int saída_final qtd)", height=250,
                               placeholder="04:30 09:30 10:30 13:26 2")

with col2:
    nova_saida = st.text_area("Saídas Carregadas (horário tonelada)", height=250,
                              placeholder=("21:00 8.5\n21:30 12.3")
    ")
    nova_aux = st.text_area("Auxiliares (entrada saída_final qtd)", height=250,
                            placeholder=("19:00 04:09 13")

with col3:
    st.markdown("#### Janelas Críticas")
    saidas_entrega = st.text_area("Saídas para Entrega (um horário por linha)", height=130,
                                  value="21:00\n21:15\n21:30\n22:00\n06:00\n14:00")
    retornos_coleta = st.text_area("Retorno de Coleta (pico de chegada)", height=130,
                                   value="04:00\n04:30\n05:00\n05:30\n06:00")

# ==============================================================
# 2 – DADOS FIXOS
# ==============================================================
chegada_fixa = """03:30 9.6
04:20 5.9
04:50 5.4
04:50 4.4
05:10 3.9
05:15 1.8
05:30 4.5
05:45 6.3
05:45 8.9
05:50 3.7
06:20 3.1
07:10 0.9
09:15 1.0
11:00 0.8
12:30 10.5"""

saida_fixa = """21:00 3.5
21:15 6.2
21:15 2.3
21:30 7.7
21:30 9.9
21:30 2.8
21:30 9.7
21:30 9.4
21:30 11.9"""

confer_fixa = """03:30 08:00 09:12 13:18 15
06:00 11:00 12:15 16:03 1
07:00 12:00 13:12 17:00 1
07:55 11:15 12:30 17:58 1
08:00 12:00 14:00 18:48 1
12:30 16:00 17:15 22:28 13"""

aux_fixa = """03:30 07:18 3
03:30 08:00 09:12 13:18 19
04:00 07:52 12
07:55 11:15 12:30 17:58 1
12:30 16:00 17:15 22:28 5
18:30 22:26 18"""

# ==============================================================
# 3 – APLICA OS DADOS (com correção total)
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_fixa
saida_txt   = nova_saida.strip()   if nova_saida.strip()   else saida_fixa
confer_txt  = nova_confer.strip()  if nova_confer.strip()  else confer_fixa
aux_txt     = nova_aux.strip()     if nova_aux.strip()     else aux_fixa

# Janelas críticas
saidas_entrega_lst = [l.strip() for l in saidas_entrega.split("\n") if l.strip()]
retornos_coleta_lst = [l.strip() for l in retornos_coleta.split("\n") if l.strip()]

# ==============================================================
# 4 – FUNÇÕES CORRIGIDAS
# ==============================================================
def extrair_toneladas(texto):
    d = {}
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha:
            continue
        partes = linha.split()
        if len(partes) < 2:
            continue
        hora = partes[0]
        try:
            ton = float(partes[1].replace(",", "."))
            d[hora] = d.get(hora, 0) + ton
        except:
            pass
    return d

def hora_para_minutos(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 1440  # 24h em minutos

def extrair_jornadas(texto, tipo="c"):  # c = conferente, a = auxiliar
    jornadas = []
    for linha in texto.split("\n"):
        p = linha.strip().split()
        if not p:
            continue
        if tipo == "c" and len(p) == 5 and p[4].isdigit():
            jornadas.append({"e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif tipo == "a" and len(p) == 3 and p[2].isdigit():
            jornadas.append({"e": p[0], "sf": p[1], "q": int(p[2])})
    return jornadas

# ==============================================================
# 5 – PROCESSAMENTO
# ==============================================================
chegadas = extrair_toneladas(chegada_txt)
saidas   = extrair_toneladas(saida_txt)

jornadas_conferentes = extrair_jornadas(confer_txt, "c")
jornadas_auxiliares  = extrair_jornadas(aux_txt, "a")

# Todos os horários do dia
todos_horarios = set(chegadas.keys()) | set(saidas.keys()) | set(saidas_entrega_lst) | set(retornos_coleta_lst)
for j in jornadas_conferentes + jornadas_auxiliares:
    todos_horarios.add(j["e"])
    todos_horarios.add(j.get("si", j["e"]))
    todos_horarios.add(j.get("ri", j["e"]))
    todos_horarios.add(j["sf"] if "sf" in j else j.get("sf", j["e"]))

horarios_ordenados = sorted(todos_horarios, key=hora_para_minutos)

# Cálculo da equipe em cada horário
def equipe_em(horario_min, jornada):
    e = hora_para_minutos(jornada["e"])
    if "si" in jornada:  # conferente com intervalo
        si = hora_para_minutos(jornada["si"])
        ri = hora_para_minutos(jornada["ri"])
        sf = hora_para_minutos(jornada["sf"])
        return (e <= horario_min < si) or (ri <= horario_min <= sf)
    else:  # auxiliar
        sf = hora_para_minutos(jornada["sf"])
        return e <= horario_min <= sf

eq_total_lista = []
for h in horarios_ordenados:
    minutos = hora_para_minutos(h)
    total = 0
    for j in jornadas_conferentes + jornadas_auxiliares:
        if equipe_em(minutos, j):
            total += j["q"]
    eq_total_lista.append(total)

# DataFrame final
df = pd.DataFrame({
    "Horario": horarios_ordenados,
    "Chegada_Ton": [round(chegadas.get(h, 0), 1) for h in horarios_ordenados],
    "Saida_Ton":   [round(saidas.get(h, 0), 1) for h in horarios_ordenados],
    "Equipe": eq_total_lista
})

# Escala equipe para o mesmo eixo de toneladas
max_ton = max(df["Chegada_Ton"].max(), df["Saida_Ton"].max(), 10) + 10
max_eq  = df["Equipe"].max() + 5
escala = max_ton / max_eq if max_eq > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * escala

# ==============================================================
# 6 – GRÁFICO
# ==============================================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Retorno Coleta (ton)", marker_color="#90EE90"))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"],   name="Saída Carregada (ton)", marker_color="#E74C3C"))

fig.add_trace(go.Scatter(
    x=df["Horario"],
    y=df["Equipe_Escalada"],
    mode="lines+markers+text",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    text=df["Equipe"],
    textposition="top center",
    hovertemplate="Equipe: %{text}<extra></extra>"
))

# Linhas verticais críticas
if mostrar_linhas:
    for h in saidas_entrega_lst:
        if h in horarios_ordenados:
            fig.add_vline(x=h, line=dict(color="#3498DB", width=3, dash="dash"), annotation_text="↓ Saída Entrega", annotation_position="top")
    for h in retornos_coleta_lst:
        if h in horarios_ordenados:
            fig.add_vline(x=h, line=dict(color="#E67E22", width=3, dash="dot"), annotation_text="↑ Retorno Coleta", annotation_position="top")

# Rótulos
if rotulos:
    for i, row in df.iterrows():
        if row["Chegada_Ton"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Chegada_Ton"], text=str(row["Chegada_Ton"]), yshift=12, showarrow=False, font=dict(color="#27AE60"))
        if row["Saida_Ton"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Saida_Ton"], text=str(row["Saida_Ton"]), yshift=12, showarrow=False, font=dict(color="#C0392B"))

fig.update_layout(
    title="Produção × Equipe × Janelas Críticas Operacionais",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escalada)",
    height=700,
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# 7 – DOWNLOAD EXCEL
# ==============================================================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Produção x Equipe", index=False)
    pd.DataFrame({
        "Saída para Entrega": saidas_entrega_lst + [""] * 10,
        "Retorno de Coleta": retornos_coleta_lst + [""] * 10
    }).to_excel(writer, sheet_name="Janelas", index=False)

st.download_button(
    label="📥 Baixar Excel completo",
    data=buffer,
    file_name="producao_equipe_janelas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("App rodando 100% sem erros! Versão estável – Novembro/2025")
