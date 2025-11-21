# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("Produção vs Equipe Disponível + Janelas Operacionais")

rotulos = st.checkbox("Mostrar rótulos nos valores", value=True)
mostrar_linhas = st.checkbox("Mostrar linhas de Saída Entrega e Retorno Coleta", value=True)

# ==============================================================
# 1 – OPÇÃO DE COLAR DADOS (SOBRESCREVE OS FIXOS)
# ==============================================================
st.markdown("### ✏️ Cole novos dados (opcional – substitui os fixos)")

col_a, col_b, col_c = st.columns(3)

with col_a:
    nova_chegada = st.text_area(
        "Chegadas (Retorno de Coleta) – horário tonelada)",
        height=250,
        placeholder="04:30 15.8\n05:00 12.4\n..."
    )
    nova_confer = st.text_area(
        "Conferentes (entrada saída_int retorno_int saída_final qtd)",
        height=250,
        placeholder="04:30 09:30 10:30 13:26 2\n19:00 23:00 00:05 04:09 8\n..."
    )

with col_b:
    nova_saida = st.text_area(
        "Saídas Carregadas (horário tonelada)",
        height=250,
        placeholder="21:00 8.5\n21:30 12.3\n..."
    )
    nova_aux = st.text_area(
        "Auxiliares (entrada saída_final qtd)",
        height=250,
        placeholder="19:00 04:09 13\n21:00 06:08 29\n..."
    )

with col_c:
    st.markdown("#### Janelas Críticas")
    saidas_entrega = st.text_area(
        "Horários de Saída para Entrega (um por linha)",
        height=120,
        value="""21:00
21:15
21:30
22:00
06:00
14:00""",
        placeholder="21:30\n22:00\n..."
    )
    retornos_coleta = st.text_area(
        "Horários de Retorno de Coleta (pico de chegada de carga)",
        height=120,
        value="""04:00
04:30
05:00
05:30
06:00""",
        placeholder="04:30\n05:00\n..."
    )

# ==============================================================
# 2 – DADOS FIXOS (usados se nada for colado)
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

saida_fixa = """04:30 0,0
05:10 0,0
06:00 0,0
14:00 0,0
21:00 3,5
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
# ==============================================================
# 3 – SUBSTITUIÇÃO DOS DADOS
# ==============================================================
chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_fixa
saida_txt = nova_saida.strip() if nova_saida.strip() else saida_fixa
confer_txt = nova_confer.strip() if nova_confer.strip() else confer_fixa
aux_txt = nova_aux.strip() if nova_aux.strip() else aux_fixa

# Novos: listas de horários críticos
lista_saida_entrega = [h.strip() for h in saidas_entrega.split("\n") if h.strip() and len(h.strip()) == 5]
lista_retorno_coleta = [h.strip() for h in retornos_coleta.split("\n") if h.strip() and len(h.strip()) == 5]

# ==============================================================
# 4 – PROCESSAMENTO DOS DADOS
# ==============================================================
def extrair_producao(texto_chegada, texto_saida):
    cheg = {}
    said = {}
    for bloco, d in [(texto_chegada, cheg), (texto_saida, said)]:
        for l in bloco.strip().split("\n"):
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
    return cheg, said

cheg, said = extrair_producao(chegada_txt, saida_txt)

def jornadas(t, tipo="c"):
    lista = []
    for l in t.strip().split("\n"):
        p = l.strip().split()
        if not p: continue
        if tipo == "c" and len(p) == 5 and p[4].isdigit():
            lista.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif tipo == "a" and len(p) == 3 and p[2].isdigit():
            lista.append({"t": "a", "e": p[0], "sf": p[1], "q": int(p[2])})
    return lista

jornadas_conf = jornadas(texto_confer, "c")
jornadas_aux = jornadas(texto_aux, "a")

def min_hora(h):
    try: hh, mm = map(int, h.split(":")); return hh*60 + mm
    except: return 1440

# Todos os horários relevantes
todas_horas = set(cheg.keys()) | set(said.keys()) | set(lista_saida_entrega) | set(lista_retorno_coleta)
horas_equipe = set()
for j in jornadas_conf + jornadas_aux:
    horas_equipe.add(j["e"])
    if j["t"] == "c":
        horas_equipe.update([j["si"], j["ri"], j["sf"]])
    else:
        horas_equipe.add(j["sf"])
todas_horas.update(horas_equipe)

horarios = sorted(todas_horas, key=min_hora)

def calcular_equipe(jornadas_list, horarios):
    tl = [min_hora(h) for h in horarios]
    eq = [0] * len(tl)
    for j in jornadas_list:
        e = min_hora(j["e"])
        if j["t"] == "c":
            si = min_hora(j["si"])
            ri = min_hora(j["ri"])
            sf = min_hora(j["sf"])
            for i, t in enumerate(tl):
                if (e <= t < si) or (ri <= t <= sf):
                    eq[i] += j["q"]
        else:
            sf = min_hora(j["sf"])
            for i, t in enumerate(tl):
                if e <= t <= sf:
                    eq[i] += j["q"]
    return eq

eq_conf = calcular_equipe(jornadas_conf, horarios)
eq_aux = calcular_equipe(jornadas_aux, horarios)
eq_total = [c + a for c, a in zip(eq_conf, eq_aux)]

# Valores por horário
cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
said_val = [round(said.get(h, 0), 1) for h in horarios]

df = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": cheg_val,
    "Saida_Ton": said_val,
    "Equipe": eq_total,
    "Equipe_Conf": eq_conf,
    "Equipe_Aux": eq_aux
})

# Escala da equipe para caber no mesmo eixo das toneladas
max_ton = max(max(cheg_val or [0]), max(said_val or [0])) + 5
max_eq = max(eq_total or [0]) + 5
scale = max_ton / max_eq if max_eq > 0 else 1
df["Equipe_Escalada"] = df["Equipe"] * scale

# ==============================================================
# GRÁFICO COM NOVAS LINHAS VERTICAIS
# ==============================================================
fig = go.Figure()

# Barras
fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada (Retorno Coleta)", marker_color="#90EE90", opacity=0.8))
fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Carregada", marker_color="#E74C3C", opacity=0.8))

# Linha da equipe
fig.add_trace(go.Scatter(
    x=df["Horario"], y=df["Equipe_Escalada"],
    mode="lines+markers+text",
    name="Equipe Disponível",
    line=dict(color="#9B59B6", width=4, dash="dot"),
    marker=dict(size=8),
    text=df["Equipe"],
    textposition="top center",
    textfont=dict(size=10, color="#9B59B6"),
    hovertemplate="Equipe: %{text}<extra></extra>"
))

# === NOVO: LINHAS VERTICAIS DE JANELAS CRÍTICAS ===
if mostrar_linhas:
    # Saídas para Entrega (prioridade máxima de carregamento)
    for hora in lista_saida_entrega:
        if hora in horarios:
            fig.add_shape(
            type="line",
            x0=hora, x1=hora,
            y0=0, y1=max_ton,
            line=dict(color="#3498DB", width=3, dash="dash"),
            name="Saída Entrega"
        )
        fig.add_annotation(
            x=hora, y=max_ton*0.95,
            text="Saída Entrega",
            showarrow=false,
            font=dict(color="#2980B9", size=11, weight="bold"),
            bgcolor="white",
            bordercolor="#3498DB",
            borderwidth=2,
            borderpad=4
        )

    # Retornos de Coleta (pico de descarregamento)
    for hora in lista_retorno_coleta:
        if hora in horarios:
            fig.add_shape(
                type="line",
                x0=hora, x1=hora,
                y0=0, y1=max_ton,
                line=dict(color="#E67E22", width=3, dash="dot"),
                name="Retorno Coleta"
            )
            fig.add_annotation(
                x=hora, y=max_ton*0.85,
                text="Retorno Coleta",
                showarrow=False,
                font=dict(color="#D35400", size=11, weight="bold"),
                bgcolor="white",
                bordercolor="#E67E22",
                borderwidth=2,
                borderpad=4
            )

# Rótulos nos valores (opcional)
if rotulos:
    for _, r in df.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=str(r["Chegada_Ton"]),
                               font=dict(color="#27AE60"), showarrow=False, yshift=10, bgcolor="white")
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=str(r["Saida_Ton"]),
                               font=dict(color="#C0392B"), showarrow=False, yshift=10, bgcolor="white")

fig.update_layout(
    title="Produção Diária x Equipe x Janelas Críticas de Operação",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton]),
    height=700,
    hovermode="x unified",
    legend=dict(x=0.01, y=1.15, orientation="h"),
    barmode="stack",
    shapes=[s for s in fig.layout.shapes],  # necessário para funcionar no Streamlit
    margin=dict(t=100)
)

st.plotly_chart(fig, use_container_width=True)

# ==============================================================
# DOWNLOAD + DADOS USADOS
# ==============================================================
out = io.BytesIO()
df_export = df[["Horario", "Chegada_Ton", "Saida_Ton", "Equipe", "Equipe_Conf", "Equipe_Aux"]].copy()
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    df_export.to_excel(writer, index=False, sheet_name="Produção x Equipe")
    # Planilha extra com janelas críticas
    pd.DataFrame({
        "Saida_Entrega": lista_saida_entrega + [""]*(20-len(lista_saida_entrega)),
        "Retorno_Coleta": lista_retorno_coleta + [""]*(20-len(lista_retorno_coleta))
    }).to_excel(writer, sheet_name="Janelas", index=False)
out.seek(0)

st.download_button(
    "Baixar Excel com Produção + Janelas Críticas",
    out,
    "producao_equipe_janelas.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Dados em uso
st.markdown("### Dados atualmente em uso")
c1, c2 = st.columns(2)
with c1:
    st.markdown("**Retorno de Coleta (Chegadas)**"); st.code(chegada_txt, language="text")
    st.markdown("**Saída Carregada**"); st.code(saida_txt, language="text")
    st.markdown("**Saídas para Entrega**"); st.code("\n".join(lista_saida_entrega), language="text")
with c2:
    st.markdown("**Conferentes**"); st.code(texto_confer, language="text")
    st.markdown("**Auxiliares**"); st.code(texto_aux, language="text")
    st.markdown("**Retorno de Coleta (horários)**"); st.code("\n".join(lista_retorno_coleta), language="text")
