# pages/1_Conferentes_vs_Auxiliares.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.title("Disponibilidade de Equipe: Conferentes vs Auxiliares")

st.markdown("**Upload de dados (Excel/CSV) ou use os dados padrão abaixo.**")

# --- Upload de arquivos ---
col1, col2 = st.columns(2)
with col1:
    uploaded_conf = st.file_uploader("Jornada Conferentes", type=["txt", "csv", "xlsx"], key="conf")
with col2:
    uploaded_aux = st.file_uploader("Jornada Auxiliares", type=["txt", "csv", "xlsx"], key="aux")

# --- Dados padrão ---
jornada_conferentes_padrao = """
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
jornada_auxiliares_padrao = """
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

# --- Leitura dos dados ---
def ler_arquivo(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, header=None)
            return '\n'.join(df.astype(str).apply(' '.join', axis=1))
        else:
            return uploaded_file.getvalue().decode("utf-8")
    return None

jornada_conferentes = ler_arquivo(uploaded_conf) or jornada_conferentes_padrao
jornada_auxiliares = ler_arquivo(uploaded_aux) or jornada_auxiliares_padrao

# ===================== FUNÇÃO: LER JORNADAS =====================
def ler_jornadas(texto):
    jornadas = []
    for linha in texto.strip().split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        partes = linha.split()
        if len(partes) == 5:
            entrada, saida_intervalo, retorno_intervalo, saida_final, qtd_str = partes
            try:
                quantidade = int(qtd_str)
                jornadas.append({
                    'tipo': 'completa',
                    'entrada': entrada,
                    'saida_intervalo': saida_intervalo,
                    'retorno_intervalo': retorno_intervalo,
                    'saida_final': saida_final,
                    'quantidade': quantidade
                })
            except ValueError:
                continue
        elif len(partes) == 3:
            entrada, saida_final, qtd_str = partes
            try:
                quantidade = int(qtd_str)
                jornadas.append({
                    'tipo': 'meia',
                    'entrada': entrada,
                    'saida_final': saida_final,
                    'quantidade': quantidade
                })
            except ValueError:
                continue
    return jornadas

# ===================== FUNÇÃO: COLETAR HORÁRIOS ÚNICOS =====================
def coletar_horarios(jornada_conferentes, jornada_auxiliares):
    horarios = {'00:00', '23:59'}
    for jornada in [jornada_conferentes, jornada_auxiliares]:
        for linha in jornada.strip().split('\n'):
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split()
            if len(partes) in (3, 5):
                horarios.update(partes[:-1])
    def hora_para_minutos(h):
        try:
            h, m = map(int, h.split(':'))
            return h * 60 + m
        except:
            return 0
    return sorted(horarios, key=hora_para_minutos)

# ===================== FUNÇÃO: CONVERTER HORA EM MINUTOS =====================
def hora_para_minutos(hora):
    try:
        h, m = map(int, hora.split(':'))
        return h * 60 + m
    except:
        return 0

# ===================== FUNÇÃO: PROCESSAR DADOS =====================
def processar_dados(jornada_conferentes, jornada_auxiliares):
    horarios_lista = coletar_horarios(jornada_conferentes, jornada_auxiliares)
    timeline_minutos = [hora_para_minutos(h) for h in horarios_lista]
    disponibilidade_conferentes = [0] * len(timeline_minutos)
    disponibilidade_auxiliares = [0] * len(timeline_minutos)
    for j in ler_jornadas(jornada_conferentes):
        if j['tipo'] == 'completa':
            entrada = hora_para_minutos(j['entrada'])
            saida_intervalo = hora_para_minutos(j['saida_intervalo'])
            retorno_intervalo = hora_para_minutos(j['retorno_intervalo'])
            saida_final = hora_para_minutos(j['saida_final'])
            for i, t in enumerate(timeline_minutos):
                if (entrada <= t < saida_intervalo) or (retorno_intervalo <= t <= saida_final):
                    disponibilidade_conferentes[i] += j['quantidade']
        else:
            entrada = hora_para_minutos(j['entrada'])
            saida_final = hora_para_minutos(j['saida_final'])
            for i, t in enumerate(timeline_minutos):
                if entrada <= t <= saida_final:
                    disponibilidade_conferentes[i] += j['quantidade']
    for j in ler_jornadas(jornada_auxiliares):
        if j['tipo'] == 'completa':
            entrada = hora_para_minutos(j['entrada'])
            saida_intervalo = hora_para_minutos(j['saida_intervalo'])
            retorno_intervalo = hora_para_minutos(j['retorno_intervalo'])
            saida_final = hora_para_minutos(j['saida_final'])
            for i, t in enumerate(timeline_minutos):
                if (entrada <= t < saida_intervalo) or (retorno_intervalo <= t <= saida_final):
                    disponibilidade_auxiliares[i] += j['quantidade']
        else:
            entrada = hora_para_minutos(j['entrada'])
            saida_final = hora_para_minutos(j['saida_final'])
            for i, t in enumerate(timeline_minutos):
                if entrada <= t <= saida_final:
                    disponibilidade_auxiliares[i] += j['quantidade']
    df = pd.DataFrame({
        'Horário': horarios_lista,
        'Conferentes': disponibilidade_conferentes,
        'Auxiliares': disponibilidade_auxiliares
    })
    return df

# --- Processamento ---
df = processar_dados(jornada_conferentes, jornada_auxiliares)

# --- Controles ---
col1, col2, col3 = st.columns([1, 1, 6])
with col1:
    mostrar_rotulos = st.checkbox("Rótulos", value=True)
with col2:
    st.markdown("**Clique no gráfico para maximizar**")

# --- Download Excel (usando openpyxl) ---
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Disponibilidade')
output.seek(0)
st.download_button(
    label="📥 Baixar Excel",
    data=output,
    file_name="disponibilidade_equipe.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Gráfico Plotly ---
fig = make_subplots()
fig.add_trace(go.Scatter(
    x=df['Horário'], y=df['Conferentes'],
    mode='lines+markers',
    name='Conferentes',
    line=dict(color='#90EE90', width=3),
    marker=dict(size=8),
    fill='tozeroy',
    fillcolor='rgba(144, 238, 144, 0.3)'
))
fig.add_trace(go.Scatter(
    x=df['Horário'], y=df['Auxiliares'],
    mode='lines+markers',
    name='Auxiliares',
    line=dict(color='#228B22', width=3),
    marker=dict(size=8, symbol='square'),
    fill='tozeroy',
    fillcolor='rgba(34, 139, 34, 0.3)'
))
# Intervalo
if '09:30' in df['Horário'].values and '10:30' in df['Horário'].values:
    fig.add_vrect(x0='09:30', x1='10:30', fillcolor="gray", opacity=0.1, line_width=0)
# Rótulos
if mostrar_rotulos:
    for _, row in df.iterrows():
        if row['Conferentes'] > 0:
            fig.add_annotation(x=row['Horário'], y=row['Conferentes'] + 0.8,
                               text=str(int(row['Conferentes'])),
                               showarrow=False, font=dict(color='#90EE90', size=10, family="bold"),
                               bgcolor="white", bordercolor='#90EE90', borderwidth=1, borderpad=4)
        if row['Auxiliares'] > 0:
            fig.add_annotation(x=row['Horário'], y=row['Auxiliares'] + 0.8,
                               text=str(int(row['Auxiliares'])),
                               showarrow=False, font=dict(color='#228B22', size=10, family="bold"),
                               bgcolor="white", bordercolor='#228B22', borderwidth=1, borderpad=4)
fig.update_layout(
    title="Disponibilidade de Equipe (00:00 - 23:59)",
    xaxis_title="Horário",
    yaxis_title="Colaboradores Disponíveis",
    legend=dict(x=0, y=1),
    hovermode="x unified",
    height=600,
    margin=dict(t=80, b=50, l=50, r=50)
)
st.plotly_chart(fig, use_container_width=True)

# --- Instruções ---
st.markdown("""
**Como usar:**
- Faça upload dos arquivos (Excel/CSV/TXT) com jornadas.
- Marque/desmarque **Rótulos** para mostrar/ocultar valores.
- Clique no ícone ⤢ (canto superior direito do gráfico) para **maximizar**.
- Clique em **📥 Baixar Excel** para exportar os dados em colunas.
""")
