# pages/5_Capacidade_x_Producao.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(layout="wide")
st.title("Capacidade x Produção")

rotulos = st.checkbox("Exibir rótulos", True)

# --- Fator dinâmico (vol/kg) ---
st.sidebar.header("Configurações")
fator_dinamico = st.sidebar.number_input(
    "Fator Dinâmico (vol/kg)",
    min_value=0.0,
    value=16.10,
    step=0.1,
    format="%.2f"
)
st.write(f"**Fator atual:** {fator_dinamico:.2f}")

# ------------------------
# Dados padrão de produção (usados quando não houver upload)
# ------------------------
padrao_producao = """Cheg. Ton.
01:00 7,278041
02:30 6,936955
03:30 0
04:00 3,542897
04:30 1,676141
05:15 14,263712
05:30 4,482417
05:50 3,695104
06:00 4,389653
06:00 3,4539
06:00 2,153276
06:00 2,852677
06:30 2,720908
07:15 6,567569
07:30 1,44941
09:30 12,076731
10:15 0,1992
11:00 1,462557
12:45 0
18:00 6,98727
21:30 2,837159
23:30 7,998834
Saida Ton.
03:15 5,618428
04:45 0
20:15 8,43512
21:00 0,909347
21:00 6,061068
21:00 3,913779
21:00 4,649687
21:00 2,756661
21:00 2,461966
21:00 1,787873
21:00 4,040584
21:00 2,996577
21:00 4,22898
21:10 5,479109
21:20 9,849377
21:30 5,961456
21:30 8,997052
22:00 0,351623
22:00 0,366688
22:00 7,782288
22:15 5,598385
23:45 18,571689
"""

# ------------------------
# Funções de leitura/parsing (mesma lógica do seu outro arquivo)
# ------------------------
def ler_producao_texto(b, f):
    if b is None:
        return f
    try:
        return b.decode("utf-8")
    except:
        df = pd.read_excel(io.BytesIO(b), header=None)
        return "\n".join(" ".join(map(str, r)) for r in df.values)


def extrair_producao(texto):
    cheg = {}
    said = {}
    modo = None
    for l in texto.strip().split("\n"):
        l = l.strip()
        if l == "Cheg. Ton.":
            modo = "cheg"; continue
        if l == "Saida Ton.":
            modo = "said"; continue
        if not l or modo is None: continue
        p = l.split()
        if len(p) < 2: continue
        h = p[0]
        try:
            v = float(p[1].replace(",", "."))
            if modo == "cheg":
                cheg[h] = cheg.get(h, 0) + v
            else:
                said[h] = said.get(h, 0) + v
        except:
            pass
    return cheg, said

# ------------------------
# Dados de capacidade (padrão)
# ------------------------
dados_capacidade = {
    "Hora": [
        "00:00","01:00","02:00","03:00","04:00","05:00","06:00","07:00",
        "08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00",
        "16:00","17:00","18:00","19:00","20:00","21:00","22:00","23:00"
    ],
    "Capacidade_kg": [
        552.1408578,552.1408578,552.1408578,552.1408578,953.1694808,953.1694808,
        1456.87693,1456.87693,1408.443521,552.1408578,48.43340858,904.7360722,
        1005.477562,1156.589797,300.2871332,300.2871332,199.5456433,300.2871332,
        1844.344199,1995.456433,2247.310158,2247.310158,1833.688849,121.0835214
    ]
}
df_cap = pd.DataFrame(dados_capacidade)
# criar dict para lookup rápido (hora cheia string -> capacidade em toneladas)
cap_dict_t = {}
for h, kg in zip(df_cap["Hora"], df_cap["Capacidade_kg"]):
    # capacidade ajustada (kg * fator) convertida para toneladas
    cap_t = (kg * fator_dinamico) / 1000.0
    cap_dict_t[h] = round(cap_t, 1)

# ------------------------
# Produção: usa session_state ou padrão (igual aos outros)
# ------------------------
if "prod_bytes" not in st.session_state:
    st.session_state.prod_bytes = None
texto_producao = ler_producao_texto(st.session_state.prod_bytes, padrao_producao)
cheg, said = extrair_producao(texto_producao)

# ------------------------
# Montar eixo X unificado (horas da capacidade + horas reais da produção)
# ------------------------
def min_hora(h):
    try:
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 0

# coletar horas únicas
horas_unicas = set()
# adicionar horas de capacidade (cheia)
horas_unicas.update(df_cap["Hora"].tolist())
# adicionar horas da produção (chegadas e saidas)
horas_unicas.update(cheg.keys())
horas_unicas.update(said.keys())

# normalizar todos os tempos para formato "HH:MM" strings
def normaliza(h):
    if isinstance(h, pd.Timestamp):
        return h.strftime("%H:%M")
    return h

horas_unicas_str = set(normaliza(h) for h in horas_unicas)
# ordenar por minutos
horarios = sorted(list(horas_unicas_str), key=min_hora)

# ------------------------
# Para cada horário unificado, pegar produção e capacidade correspondente
# capacidade em um horário t = capacidade do hour_floor (ex: 01:15 -> 01:00)
# ------------------------
def hour_floor(h):
    mm = min_hora(h)
    hh = mm // 60
    return f"{hh:02d}:00"

prod_cheg_vals = []
prod_said_vals = []
cap_vals = []
for h in horarios:
    prod_cheg_vals.append(round(cheg.get(h, 0), 1))
    prod_said_vals.append(round(said.get(h, 0), 1))
    hf = hour_floor(h)
    cap_vals.append(cap_dict_t.get(hf, 0.0))

# Cria DataFrame final para exibição
df_final = pd.DataFrame({
    "Horario": horarios,
    "Chegada_Ton": prod_cheg_vals,
    "Saida_Ton": prod_said_vals,
    "Capacidade (t)": cap_vals
})

# ------------------------
# Plotly: barras empilhadas (Chegada / Saida) + linha de capacidade (degraus)
# ------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_final["Horario"], y=df_final["Chegada_Ton"],
    name="Chegada (ton)", marker_color="#90EE90", opacity=0.85
))

fig.add_trace(go.Bar(
    x=df_final["Horario"], y=df_final["Saida_Ton"],
    name="Saida (ton)", marker_color="#E74C3C", opacity=0.85
))

# Para desenhar degraus corretamente, extendo os pontos de capacidade adicionando o primeiro e último ponto
# Mas aqui basta usar shape='hv' em Scatter e passar a capacidade alinhada ao mesmo eixo X.
fig.add_trace(go.Scatter(
    x=df_final["Horario"], y=df_final["Capacidade (t)"],
    name="Capacidade (t)",
    mode="lines",
    line=dict(color="#9B59B6", width=4),
    hovertemplate="Capacidade: %{y:.1f} t<extra></extra>",
    connectgaps=True
))

# Ajustar shape para degrau horizontal-vertical
# plotly tem 'line.shape' no dict da trace; para barras + degrau usamos uma segunda scatter com duplicated x for step
# melhor: construir x_step e y_step para 'hv' visual manual
x_step = []
y_step = []
for i, h in enumerate(df_final["Horario"]):
    x_step.append(h)
    y_step.append(df_final["Capacidade (t)"].iloc[i])
    # lookahead: se tiver próximo, repeat current x to create vertical step when plotly draws with 'lines'
    if i + 1 < len(df_final):
        x_step.append(df_final["Horario"].iloc[i+1])
        y_step.append(df_final["Capacidade (t)"].iloc[i])

# remover a scatter anterior e adicionar a de steps
fig.data = fig.data[:-1]  # remove última trace adicionada
fig.add_trace(go.Scatter(
    x=x_step,
    y=y_step,
    name="Capacidade (t)",
    mode="lines",
    line=dict(color="#9B59B6", width=4),
    hovertemplate="Capacidade: %{y:.1f} t<extra></extra>"
))

# Rótulos (opcional) — escrevo apenas nos horários da produção (para não poluir)
if rotulos:
    for _, r in df_final.iterrows():
        if r["Chegada_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"],
                text=f"{r['Chegada_Ton']:.1f}", font=dict(color="#90EE90", size=9),
                bgcolor="white", bordercolor="#90EE90", borderwidth=1,
                showarrow=False, yshift=10)
        if r["Saida_Ton"] > 0:
            fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"],
                text=f"{r['Saida_Ton']:.1f}", font=dict(color="#E74C3C", size=9),
                bgcolor="white", bordercolor="#E74C3C", borderwidth=1,
                showarrow=False, yshift=10)
    # rótulos da capacidade só nas horas cheias (evita repetição)
    for h in df_cap["Hora"].tolist():
        hstr = h  # já em "HH:MM"
        val = cap_dict_t.get(hstr, 0.0)
        fig.add_annotation(x=hstr, y=val,
            text=f"{val:.1f}", font=dict(color="#9B59B6", size=9),
            bgcolor="white", bordercolor="#9B59B6", borderwidth=1,
            showarrow=False, yshift=0)

# Layout
max_y = max(df_final["Capacidade (t)"].max(), df_final["Chegada_Ton"].max() + df_final["Saida_Ton"].max()) * 1.15
fig.update_layout(
    xaxis_title="Horario",
    yaxis=dict(title="Toneladas", range=[0, max_y]),
    height=650,
    hovermode="x unified",
    legend=dict(x=0, y=1.05, orientation="h"),
    barmode="stack",
    margin=dict(l=60, r=60, t=40, b=60),
    plot_bgcolor="white",
)

st.plotly_chart(fig, use_container_width=True)

# Exibir dados
with st.expander("📋 Dados consolidados"):
    st.dataframe(df_final.style.format({
        "Chegada_Ton": "{:,.1f}",
        "Saida_Ton": "{:,.1f}",
        "Capacidade (t)": "{:,.1f}"
    }))
