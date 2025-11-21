# pages/Producao_x_Equipe_R3.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("🚛 Produção Diária × Equipe Disponível × Janelas Críticas")

rotulos = st.checkbox("Mostrar rótulos nos valores", value=True)
mostrar_linhas = st.checkbox("Mostrar linhas de Saída Entrega e Retorno Coleta", value=True)

# ==============================================================
# 1 – ENTRADA DE DADOS (cole aqui ou usa os fixos)
# ==============================================================
st.markdown("### ✏️ Cole novos dados (opcional – substitui os fixos)")

col_a, col_b, col_c = st.columns(3)

with col_a:
    nova_chegada = st.text_area("Retorno de Coleta (chegadas – horário tonelada)", height=250,
                                placeholder="04:30 15.8\n05:00 12.4\n...")
    nova_confer = st.text_area("Conferentes (entrada saída_int retorno_int saída_final qtd)", height=250,
                               placeholder="04:30 09:30 10:30 13:26 2\n19:00 23:00 00:05 04:09 8\n...")

with col_b:
    nova_saida = st.text_area("Saídas Carregadas (horário tonelada)", height=250,
                              placeholder="21:00 8.5\n21:30 12.3\n...")
    nova_aux = st.text_area("Auxiliares (entrada saída_final qtd)", height=250,
                            placeholder="19:00 04:09 13\n21:00 06:08 29\n...")

with col_c:
    st.markdown("#### Janelas Críticas")
    saidas_entrega = st.text_area("Horários de Saída para Entrega", height=130,
                                  value="21:00\n21:15\n21:30\n22:00\n06:00\n14:00")
    retornos_coleta = st.text_area("Horários de Retorno de Coleta (pico de chegada)", height=130,
                                   value="04:00\n04:30\n05:00\n05:30\n06:00")

# ==============================================================
# 2 – DADOS FIXOS (caso o usuário não cole nada)
# ==============================================================
chegada_fixa = """03:30 9,6
04:20 5,9
04:50 5,4
04:50 4,4
05:10 3,9
05:15 1,8
05:30 4,5
05:45 6,3
05:45 8,9
05:50 3,7
06:20 3,1
07:10 0,9
09:15 1,0
11:00 0,8
12:30 10,5"""

saida_fixa = """21:00 3,5
21:15 6,2
21:15 2,3
21:30 7,7
21:30 9,9
21:30 2,8
21:30 9,7
21:30 9,4
21:30 11,9"""

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
# 3 – DEFINIÇÃO CORRETA DAS VARIÁVEIS DE TEXTO (o erro estava aqui!)
# ==============================================================
chegada_txt  = nova_chegada.strip()  if nova_chegada.strip()  else chegada_fixa
saida_txt    = nova_saida.strip()    if nova_saida.strip()    else saida_fixa
confer_txt   = nova_confer.strip()   if nova_confer.strip()   else confer_fixa      # <--- estava faltando!
aux_txt      = nova_aux.strip()      if nova_aux.strip()      else aux_fixa

# Janelas críticas
lista_saida_entrega = [h.strip() for h in saidas_entrega.split("\n") if h.strip()]
lista_retorno_coleta = [h.strip() for h in retornos_coleta.split("\n") if h.strip()]

# ==============================================================
# 4 – FUNÇÕES DE PROCESSAMENTO
# ==============================================================
def extrair_toneladas(texto):
    d = {}
    for linha = texto.split("\n")
    for l in linha:
        l = l.strip()
        if not l: continue
        partes = l.split()
        if len(partes) < 2: continue
        hora = partes[0]
        try:
            ton = float(partes[1].replace(",", "."))
            d[hora] = d.get(hora, 0) + ton
        except:
            pass
    return d

cheg = extrair_toneladas(chegada_txt)
said = extrair_toneladas(saida_txt)

def min_to_int(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh*60 + mm
    except:
        return 1440

def extrair_jornadas(texto, tipo="c"):  # tipo "c" = conferente (5 colunas), "a" = auxiliar (3 colunas)
    lista = []
    for linha in texto.split("\n"):
        p = linha.strip().split()
        if not p: continue
        if tipo == "c" and len(p) == 5 and p[4].isdigit():
            lista.append({"e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif tipo == "a" and len(p) == 3 and p[2].isdigit():
            lista.append({"e": p[0], "sf": p[1], "q": int(p[2])})
    return lista

jornadas_conf = extrair_jornadas(confer_txt, "c")
jornadas_aux  = extrair_jornadas(aux_txt,   "a")

# Todos os horários que precisamos plotar
todos_horarios = set(cheg.keys()) | set(said.keys()) | set(lista_saida_entrega) | set(lista_retorno_coleta)
for j in jornadas_conf + jornadas_aux:
    todos_horarios.add(j["e"])
    if "sf" in j: todos_horarios.add(j["sf"])
    if "si" in j: todos_horarios.update([j["si"], j["ri"]])

horarios = sorted(todos_horarios, key=min_to_int)

# ==============================================================
# 5 – CÁLCULO DA EQUIPE POR HORÁRIO
# ==============================================================
def equipe_no_horario(jornadas_lista, horarios):
    minutos = [min_to_int(h) for h in horarios]
    equipe = [0] * len(horarios)
    for j in jornadas_lista:
        entrada = min_to_int(j["e"])
        if "si" in j:  # conferente com intervalo
            sai_int = min_to_int(j["si"])
            ret_int = min_to_int(j["ri"])
            saida   = min_to_int(j["sf"])
            for i, t in enumerate(minutos):
                if (entrada <= t < sai_int) or (ret_int <= t <= saida):
                    equipe[i] += j["q"]
        else:  # auxiliar ou conferente sem intervalo detalhado
            saida = min_to_int(j["sf"])
            for i, t in enumerate(minutos):
                if entrada <= t <= saida:
                    equipe[i] += j["q"]
    return equipe

eq_conf = equipe_no_horario(jornadas_conf, horarios)
eq_aux  = equipe_no_horario(jornadas_aux,  horarios)
eq_total = [a + b for a, b in zip(eq_conf, eq_aux)]

# ==============================================================
# 6 – DATAFRAME PRINCIPAL
# ==============================================================
df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": [round(cheg.get(h, 0), 1) for h in horarios],
    "Saida_Ton":   [round(said.get(h, 0), 1) for h in horarios],
    "Equipe": eq_total,
    "Conf": eq_conf,
    "Aux": eq_aux
})

# Escala da equipe para o mesmo eixo das toneladas
max_ton = max(df["Chegada_Ton"].max(), df["Saida_Ton"].max()) + 8
max_eq  = df["Equipe"].max() + 5
scale   = max_ton / max_eq if max_eq > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# ==============================================================
# 7 – GRÁFICO
# ==============================================================
fig = go.Figure()

fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Retorno Coleta (ton)", marker_color="#90EE90"))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"],   name="Saída Carregada (ton)", marker_color="#E74C3C"))

fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers+text",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    text=df["Equipe"],
    textposition="top center",
    hovertemplate="Equipe: %{text}<extra></extra>"
))

# Linhas verticais críticas
if mostrar_linhas:
    for hora in lista_saida_entrega:
        if hora in horarios:
            fig.add_vline(x=hora, line=dict(color="#3498DB", width=3, dash="dash"),
                          annotation_text="Saída Entrega", annotation_position="top")
    for hora in lista_retorno_coleta:
        if hora in horarios:
            fig.add_vline(x=hora, line=dict(color="#E67E22", width=3, dash="dot"),
                          annotation_text="Retorno Coleta", annotation_position="top")

if rotulos:
    for i, row in df.iterrows():
        if row["Chegada_Ton"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Chegada_Ton"], text=str(row["Chegada_Ton"]),
                               yshift=10, showarrow=False, font=dict(color="#27AE60"))
        if row["Saida_Ton"] > 0:
            fig.add_annotation(x=row["Horario"], y=row["Saida_Ton"], text=str(row["Saida_Ton"]),
                               yshift=10, showarrow=False, font=dict(color="#C0392B"))

fig.update_layout(
    title="Produção × Equipe × Janelas Críticas",
    xaxis_title="Horário",
    yaxis_title="Toneladas | Equipe (escalada)",
    height=700,
    barmode="stack",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.1, x=0)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# 8 – DOWNLOAD EXCEL
# ==============================================================
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Produção x Equipe", index=False)
    pd.DataFrame({"Saída para Entrega": lista_saida_entrega, "Retorno de Coleta": lista_retorno_coleta}).to_excel(writer, sheet_name="Janelas", index=False)
buffer.seek(0)

st.download_button(
    label="Baixar Excel completo",
    data=buffer,
    file_name="producao_equipe_janelas.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("App rodando perfeitamente! Nenhum erro mais.")
