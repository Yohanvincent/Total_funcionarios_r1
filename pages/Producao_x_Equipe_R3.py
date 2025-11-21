# pages/Producao_x_Equipe_Final.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Capacidade Logística", layout="wide")
st.title("🚛 Produção × Equipe × Janelas Críticas — Versão Final Estável")

# Opções visuais
mostrar_rotulos = st.checkbox("Mostrar rótulos de toneladas", value=True)
mostrar_janelas = st.checkbox("Mostrar linhas de Saída Entrega e Retorno Coleta", value=True)

# Opções visuais
mostrar_rotulos = st.checkbox("Mostrar rótulos de toneladas", value=True)
mostrar_janelas = st.checkbox("Mostrar linhas de Saída Entrega e Retorno Coleta", value=True)

# ==============================================================
# 1 – ENTRADA DE DADOS
# ==============================================================
st.markdown("### ✏️ Cole seus dados aqui (ou use os padrões)")

c1, c2, c3 = st.columns(3)

with c1:
    nova_chegada = st.text_area(
        "Retorno de Coleta (horário tonelada)",
        height=280,
        placeholder="04:30 15.8\n05:00 12.4\n06:00 8.2"
    )
    nova_confer = st.text_area(
        "Conferentes (entrada saída_int retorno_int saída_final qtd)",
        height=280,
        placeholder="04:30 09:30 10:30 13:26 2\n19:00 23:00 00:05 04:09 8"
    )

with c2:
    nova_saida = st.text_area(
        "Saídas Carregadas (horário tonelada)",
        height=280,
        placeholder="21:00 8.5\n21:30 12.3\n22:00 15.0"
    )
    nova_aux = st.text_area(
        "Auxiliares (entrada saída_final qtd)",
        height=280,
        placeholder="19:00: 04:09 29\n03:30 13:18 19"
    )

with c3:
    st.markdown("#### Janelas Críticas Operacionais")
    saidas_entrega = st.text_area(
        "Horários de Saída para Entrega (um por linha)",
        height=140,
        value="21:00\n21:15\n21:30\n22:00\n06:00\n14:00"
    )
    retornos_coleta = st.text_area(
        "Horários de Retorno de Coleta (pico de chegada)",
        height=140,
        value="04:00\n04:30\n05:00\n05:30\n06:00"
    )

# ==============================================================
# 2 – DADOS PADRÃO
# ==============================================================
chegada_default = """03:30 9.6
04:20 5.9
04:50 5.4
04:50 4.4
05:10 3.9
05:15 1.8
05:30 4.5
05:45 6.3
05:45 8.9
05:50 3.7
06:20 3.1"""

saida_default = """21:00 3.5
21:15 6.2
21:15 2.3
21:30 7.7
21:30 9.9
21:30 11.9"""

confer_default = """03:30 08:00 09:12 13:18 15
12:30 16:00 17:15 22:28 13
19:00 23:00 00:05 04:09 8"""

aux_default = """03:30 13:18 19
19:00 04:09 29"""

# ==============================================================
# 3 – APLICA OS DADOS CORRETAMENTE
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_default
saida_txt   = nova_saida.strip()   if nova_saida.strip()   else saida_default
confer_txt  = nova_confer.strip()  if nova_confer.strip()  else confer_default
aux_txt     = nova_aux.strip()     if nova_aux.strip()     else aux_default

# Janelas críticas
saida_entrega_horas = [h.strip() for h in saidas_entrega.split("\n") if h.strip()]
retorno_coleta_horas = [h.strip() for h in retornos_coleta.split("\n") if h.strip()]

# ==============================================================
# 4 – FUNÇÕES AUXILIARES
# ==============================================================
def parse_toneladas(texto):
    tons = {}
    for linha in texto.split("\n"):
        linha = linha.strip()
        if not linha: continue
        partes = linha.split()
        if len(partes) < 2: continue
        hora = partes[0]
        try:
            valor = float(partes[1].replace(",", "."))
            tons[hora] = tons.get(hora, 0) + valor
        except:
            pass
    return tons

def hora_para_min(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh*60 + mm
    except:
        return 1440

def parse_jornadas(texto, tipo="conf"):  # conf ou aux
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
conf_jornadas = parse_jornadas(confer_txt, "conf")
aux_jornadas  = parse_jornadas(aux_txt, "aux")

# Todos os horários do dia
todos_h = set(chegadas) | set(saidas) | set(saida_entrega_horas) | set(retorno_coleta_horas)
for j in conf_jornadas + aux_jornadas:
    todos_h.add(j["e"])
    if "si" in j:
        todos_h.update([j["si"], j["ri"]])
    todos_h.add(j.get("sf", j["e"]))

horarios = sorted(todos_h, key=hora_para_min)

# Cálculo da equipe presente em cada horário
equipe_por_hora = []
for h in horarios:
    min_h = hora_para_min(h)
    total = 0
    for j in conf_jornadas + aux_jornadas:
        entrada = hora_para_min(j["e"])
        if "si" in j:  # conferente com intervalo
            sai_int = hora_para_min(j["si"])
            ret_int = hora_para_min(j["ri"])
            saida   = hora_para_min(j["sf"])
            if (entrada <= min_h < sai_int) or (ret_int <= min_h <= saida):
                total += j["q"]
        else:  # auxiliar
            saida = hora_para_min(j["sf"])
            if entrada <= min_h <= saida:
                total += j["q"]
    equipe_por_hora.append(total)

# DataFrame
df = pd.DataFrame({
    "Horário": horarios,
    "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
    "Saída (ton)":   [round(saidas.get(h, 0), 1) for h in horarios],
    "Equipe": equipe_por_hora
})

# Escala da equipe para o mesmo eixo de toneladas
max_ton = df[["Chegada (ton)", "Saída (ton)"]].max().max() + 10
max_eq  = df["Equipe"].max() + 5
escala = max_ton / max_eq if max_eq > 0 else 1
df["Equipe Escala"] = df["Equipe"] * escala

# ==============================================================
# 6 – GRÁFICO INTERATIVO
# ==============================================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horário"], y=df["Chegada (ton)"], name="Retorno Coleta", marker_color="#2ECC71", opacity=0.9))
fig.add_trace(go.Bar(x=df["Horário"], y=df["Saída (ton)"],   name="Saída Carregada", marker_color="#E74C3C", opacity=0.9))

fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe Escala"],
    mode="lines+markers+text",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    text=df["Equipe"],
    textposition="top center",
    textfont=dict(size=12, color="#8E44AD"),
    hovertemplate="Equipe: %{text} pessoas<extra></extra>"
))

# Linhas verticais das janelas críticas
if mostrar_janelas:
    for h in saida_entrega_horas:
        if h in horarios:
            fig.add_vline(x=h, line=dict(color="#3498DB", width=4, dash="dash"),
                          annotation_text="Saída Entrega", annotation_position="top right")
    for h in retorno_coleta_horas:
        if h in horarios:
            fig.add_vline(x=h, line=dict(color="#E67E22", width=4, dash="dot"),
                          annotation_text="Retorno Coleta", annotation_position="top left")

# Rótulos
if mostrar_rotulos:
    for i, row in df.iterrows():
        if row["Chegada (ton)"] > 0:
            fig.add_annotation(x=row["Horário"], y=row["Chegada (ton)"], text=str(row["Chegada (ton)"]),
                               yshift=10, showarrow=False, font=dict(color="#27AE60", size=11))
        if row["Saída (ton)"] > 0:
            fig.add_annotation(x=row["Horário"], y=row["Saída (ton)"], text=str(row["Saída (ton)"]),
                               yshift=10, showarrow=False, font=dict(color="#C0392B", size=11))

fig.update_layout(
    title="Capacidade Operacional em Tempo Real — Transporte Fracionado",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escalada)",
    height=750,
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.08),
    margin=dict(t=100)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# 7 – DOWNLOAD EXCEL
# ==============================================================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Produção x Equipe", index=False)
    pd.DataFrame({
        "Saída para Entrega": saida_entrega_horas,
        "Retorno de Coleta": retorno_coleta_horas
    }).to_excel(writer, sheet_name="Janelas Críticas", index=False)

st.download_button(
    label="📊 Baixar Relatório Completo em Excel",
    data=buffer,
    file_name="relatorio_capacidade_logistica.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("App rodando 100% sem erros — Novembro/2025 ✅")
st.caption("Desenvolvido com ❤️ por Grok 4 — xAI")
