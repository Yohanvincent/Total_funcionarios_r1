# pages/05-Auxiliar_x_Conferente.py
# =============================================
# OBJETIVO: Comparar disponibilidade de Conferentes vs Auxiliares
# LAYOUT:
# 1. Título + Checkbox
# 2. CAMPOS PARA COLAR JORNADAS (Conferentes + Auxiliares)
# 3. Gráfico
# 4. Botão Baixar Excel
# 5. Dados colados (visualização)
# 6. Explicação de formato
# =============================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# =============================================
# 1. CONFIGURAÇÃO DA PÁGINA
# =============================================
st.set_page_config(layout="wide")
st.title("Disponibilidade: Auxiliares Carga/Descarga x Conferentes")
rotulos = st.checkbox("Rótulos", True)

# =============================================
# 2. PERSISTÊNCIA DE DADOS COLADOS (session_state)
# =============================================
if "jornada_conf" not in st.session_state:
    st.session_state.jornada_conf = ""
if "jornada_aux" not in st.session_state:
    st.session_state.jornada_aux = ""

# =============================================
# 3. CAMPOS PARA COLAR JORNADAS
# =============================================
st.markdown("### Cole as jornadas (uma por linha, separadas por espaço)")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Conferentes**")
    jornada_conf = st.text_area(
        "Cole aqui os dados de Conferentes",
        value=st.session_state.jornada_conf,
        height=280,
        placeholder="01:00 04:00 05:05 10:23 1\n16:00 20:00 21:05 01:24 2\n...",
        key="input_conf_page"
    )
    if jornada_conf != st.session_state.jornada_conf:
        st.session_state.jornada_conf = jornada_conf
        st.success("Conferentes atualizados!")

with col_b:
    st.markdown("**Auxiliares**")
    jornada_aux = st.text_area(
        "Cole aqui os dados de Auxiliares",
        value=st.session_state.jornada_aux,
        height=280,
        placeholder="16:00 20:00 21:05 01:24 5\n18:00 22:00 23:00 03:12 1\n...",
        key="input_aux_page"
    )
    if jornada_aux != st.session_state.jornada_aux:
        st.session_state.jornada_aux = jornada_aux
        st.success("Auxiliares atualizados!")

st.markdown("<br>", unsafe_allow_html=True)

# =============================================
# 4. VERIFICAR SE DADOS FORAM COLADOS
# =============================================
jc = st.session_state.jornada_conf.strip()
ja = st.session_state.jornada_aux.strip()

if not jc or not ja:
    st.warning("Cole as jornadas nos campos acima para gerar o gráfico.")
    st.stop()

# =============================================
# 5. FUNÇÕES AUXILIARES
# =============================================
def minutos(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 0

def extrair_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split("\n"):
        p = linha.strip().split()
        if len(p) == 5 and p[4].isdigit():
            jornadas.append({"tipo": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            jornadas.append({"tipo": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
    return jornadas

# =============================================
# 6. COLETAR HORÁRIOS + TIMELINE
# =============================================
horas_set = set()
max_min = 0
for texto in [jc, ja]:
    for linha in texto.strip().split("\n"):
        p = linha.strip().split()
        if len(p) in (3, 5):
            for h in p[:-1]:
                m = minutos(h)
                if m < minutos(p[0]):
                    m += 1440
                horas_set.add(h)
                max_min = max(max_min, m)

timeline_horas = []
current = 0
while current <= max_min + 60:
    total_min = current % 1440
    hh = total_min // 60
    mm = total_min % 60
    hora_str = f"{hh:02d}:{mm:02d}"
    timeline_horas.append(hora_str)
    current += 15

todos_horarios = sorted(set(timeline_horas + list(horas_set)), key=minutos)

timeline_min = []
for h in todos_horarios:
    m = minutos(h)
    if len(timeline_min) > 0 and m < timeline_min[0] and m >= 0:
        m += 1440
    timeline_min.append(m)

horarios = [h for _, h in sorted(zip(timeline_min, todos_horarios))]
timeline_min = sorted(timeline_min)

# =============================================
# 7. CONTAGEM DE FUNCIONÁRIOS
# =============================================
conf = [0] * len(timeline_min)
aux = [0] * len(timeline_min)

def aplicar_jornada_com_cruzamento(j, tl_vals, contador):
    e = minutos(j["e"])
    sf = minutos(j.get("sf", j.get("si", "")))
    si = minutos(j.get("si", "")) if "si" in j else -1
    ri = minutos(j.get("ri", "")) if "ri" in j else -1

    if sf < e: sf += 1440
    if si != -1 and si < e: si += 1440
    if ri != -1 and ri < e: ri += 1440

    for i, t in enumerate(tl_vals):
        t_adj = t + (1440 if t < e else 0)
        active = False
        if si == -1:
            active = e <= t_adj <= sf
        else:
            active = (e <= t_adj < si) or (ri <= t_adj <= sf)
        if active:
            contador[i] += j["q"]

for j in extrair_jornadas(jc):
    aplicar_jornada_com_cruzamento(j, timeline_min, conf)
for j in extrair_jornadas(ja):
    aplicar_jornada_com_cruzamento(j, timeline_min, aux)

conf = [int(x) for x in conf]
aux = [int(x) for x in aux]

# =============================================
# 8. DATAFRAME
# =============================================
df = pd.DataFrame({
    "Horario": horarios,
    "Conferentes": conf,
    "Auxiliares": aux
})

# =============================================
# 9. GRÁFICO
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
    fig.add_vrect(x0="09:30", x1="10:30", fillcolor="gray", opacity=0.1, layer="below")

if rotulos:
    for _, r in df.iterrows():
        if r["Conferentes"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Conferentes"] + 0.8,
                text=f"<b>{r['Conferentes']}</b>",
                showarrow=False,
                font=dict(color="#90EE90", size=10),
                bgcolor="white", bordercolor="#90EE90", borderwidth=1, borderpad=4
            )
        if r["Auxiliares"] > 0:
            fig.add_annotation(
                x=r["Horario"], y=r["Auxiliares"] + 0.8,
                text=f"<b>{r['Auxiliares']}</b>",
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
    legend=dict(x=0, y=1),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

# =============================================
# 10. BAIXAR EXCEL
# =============================================
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False)
output.seek(0)
st.download_button(
    "Baixar Excel",
    output,
    "equipe_disponibilidade.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================
# 11. VISUALIZAÇÃO DOS DADOS COLADOS
# =============================================
st.markdown("### Dados colados")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Conferentes**")
    st.code(jc, language="text")
with col2:
    st.markdown("**Auxiliares**")
    st.code(ja, language="text")

# =============================================
# 12. EXPLICAÇÃO
# =============================================
with st.expander("Como preparar os dados"):
    st.markdown(
        "### Formato das linhas:\n\n"
        "| Tipo | Exemplo |\n"
        "|------|---------|\n"
        "| Completa | `23:30 03:30 04:35 08:49 19` |\n"
        "| Meia | `19:00 22:52 12` |\n\n"
        "- Horário: `HH:MM` (24h)\n"
        "- Jornadas que cruzam meia-noite são **suportadas**\n"
        "- Quantidade no final (inteiro)\n"
        "- Separado por **espaços**\n"
        "- **Cole diretamente no campo acima**\n\n"
        "> **Dica:** Copie do Excel → Cole aqui → Pronto!"
    )
