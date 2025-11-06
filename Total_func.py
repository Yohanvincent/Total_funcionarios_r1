# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Logístico", layout="wide")

# ===================== DADOS DE ENTRADA =====================
jornada_conferentes = """
00:00 04:00 05:15 09:33 9
04:00 09:00 10:15 13:07 27
04:30 08:30 10:30 15:14 1
06:00 11:00 12:15 16:03 1
07:45 12:00 13:15 17:48 1
08:00 12:00 13:15 18:03 2
10:00 12:00 14:00 20:48 11
12:00 16:00 17:15 22:02 8
13:00 16:00 17:15 22:55 5
15:45 18:00 18:15 22:00 7
16:30 19:30 19:45 22:39 2
"""

jornada_auxiliares = """
00:00 04:00 05:15 09:33 10
04:00 09:00 10:15 13:07 17
12:00 16:00 17:15 22:02 2
13:00 16:00 17:15 22:55 3
15:45 18:00 18:15 22:00 3
16:30 19:30 19:45 22:39 2
17:48 21:48 1
18:00 22:00 19
19:00 22:52 5
"""

# ===================== FUNÇÃO: LER JORNADAS =====================
def ler_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        partes = linha.split()
        if len(partes) == 5:
            entrada, saida_int, retorno_int, saida_final, qtd = partes
            try:
                quantidade = int(qtd)
                jornadas.append({
                    'tipo': 'completa',
                    'entrada': entrada,
                    'saida_intervalo': saida_int,
                    'retorno_intervalo': retorno_int,
                    'saida_final': saida_final,
                    'quantidade': quantidade
                })
            except:
                continue
        elif len(partes) == 3:
            entrada, saida_final, qtd = partes
            try:
                quantidade = int(qtd)
                jornadas.append({
                    'tipo': 'meia',
                    'entrada': entrada,
                    'saida_final': saida_final,
                    'quantidade': quantidade
                })
            except:
                continue
    return jornadas

# ===================== FUNÇÃO: COLETAR HORÁRIOS =====================
def coletar_horarios(j1, j2):
    horarios = set()
    for texto in [j1, j2]:
        for linha in texto.strip().split('\n'):
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split()
            if len(partes) in (3, 5):
                horarios.update(partes[:-1])
    return sorted(horarios, key=lambda x: int(x.split(':')[0])*60 + int(x.split(':')[1]))

# ===================== FUNÇÃO: HORA → DATETIME =====================
def hora_para_datetime(hora_str, base_date="2025-01-01"):
    h, m = map(int, hora_str.split(':'))
    return datetime.strptime(f"{base_date} {h:02d}:{m:02d}", "%Y-%m-%d %H:%M")

# ===================== PROCESSAMENTO =====================
horarios_lista = coletar_horarios(jornada_conferentes, jornada_auxiliares)
timeline = [hora_para_datetime(h) for h in horarios_lista]

total_funcionarios = [0] * len(timeline)

def processar_jornada(j, total_list, timeline_list):
    if j['tipo'] == 'completa':
        e = hora_para_datetime(j['entrada'])
        si = hora_para_datetime(j['saida_intervalo'])
        ri = hora_para_datetime(j['retorno_intervalo'])
        sf = hora_para_datetime(j['saida_final'])
        for i, t in enumerate(timeline_list):
            if (e <= t < si) or (ri <= t <= sf):
                total_list[i] += j['quantidade']
    else:
        e = hora_para_datetime(j['entrada'])
        sf = hora_para_datetime(j['saida_final'])
        for i, t in enumerate(timeline_list):
            if e <= t <= sf:
                total_list[i] += j['quantidade']

# Processa conferentes e auxiliares
for j in ler_jornadas(jornada_conferentes):
    processar_jornada(j, total_funcionarios, timeline)
for j in ler_jornadas(jornada_auxiliares):
    processar_jornada(j, total_funcionarios, timeline)

# DataFrame
df = pd.DataFrame({
    'Horário': [t.strftime("%H:%M") for t in timeline],
    'Total Funcionários': total_funcionarios,
    'Datetime': timeline
})

# ===================== GRÁFICO COM PLOTLY =====================
st.title("Disponibilidade Total de Funcionários")

# Botão para rótulos
mostrar_rotulos = st.checkbox("Mostrar rótulos", value=True)

fig = go.Figure()

# Linha principal
fig.add_trace(go.Scatter(
    x=df['Datetime'],
    y=df['Total Funcionários'],
    mode='lines+markers',
    name='Total Funcionários',
    line=dict(color='#90EE90', width=4),
    marker=dict(size=8, symbol='diamond'),
    fill='tozeroy',
    fillcolor='rgba(144, 238, 144, 0.3)'
))

# Intervalo 09:30 - 10:30
if '09:30' in df['Horário'].values and '10:30' in df['Horário'].values:
    t1 = df[df['Horário'] == '09:30']['Datetime'].iloc[0]
    t2 = df[df['Horário'] == '10:30']['Datetime'].iloc[0]
    fig.add_vrect(x0=t1, x1=t2, fillcolor="gray", opacity=0.1, line_width=0, annotation_text="Intervalo")

# Rótulos
if mostrar_rotulos:
    for _, row in df.iterrows():
        if row['Total Funcionários'] > 0:
            fig.add_annotation(
                x=row['Datetime'],
                y=row['Total Funcionários'] + 1,
                text=str(int(row['Total Funcionários'])),
                showarrow=False,
                font=dict(color='#90EE90', size=10, family="Arial"),
                bgcolor="white",
                bordercolor='#90EE90',
                borderwidth=1,
                borderpad=4
            )

fig.update_layout(
    title="Disponibilidade Total de Funcionários (Conferentes + Auxiliares)",
    xaxis_title="Horário",
    yaxis_title="Funcionários Disponíveis",
    xaxis=dict(
        tickmode='array',
        tickvals=df['Datetime'],
        ticktext=df['Horário'],
        tickangle=45
    ),
    hovermode="x unified",
    template="simple_white",
    height=600,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

# ===================== INSTRUÇÕES =====================
with st.expander("Como usar"):
    st.markdown("""
    - **Zoom**: Arraste no gráfico  
    - **Rótulos**: Marque/desmarque a caixa acima  
    - **Hover**: Passe o mouse para ver detalhes  
    - **Responsivo**: Funciona em celular e desktop
    """)
