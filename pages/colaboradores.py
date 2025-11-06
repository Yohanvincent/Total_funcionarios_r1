import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.title("Disponibilidade de Equipe: Conferentes vs Auxiliares")
st.markdown("**Upload de dados (Excel/CSV/TXT) ou use os dados padrão.**")

col1, col2 = st.columns(2)
with col1:
    uploaded_conf = st.file_uploader("Jornada Conferentes", type=["txt", "csv", "xlsx"], key="conf")
with col2:
    uploaded_aux = st.file_uploader("Jornada Auxiliares", type=["txt", "csv", "xlsx"], key="aux")

jornada_conferentes_padrao = """00:00 04:00 05:15 09:33 9
04:00 09:00 10:15 13:07 27
04:30 08:30 10:30 15:14 1
06:00 11:00 12:15 16:03 1
07:45 12:00 13:15 17:48 1
08:00 12:00 13:15 18:03 2
10:00 12:00 14:00 20:48 11
12:00 16:00 17:15 22:02 8
13:00 16:00 17:15 22:55 5
15:45 18:00 18:15 22:00 7
16:30 19:30 19:45 22:39 2"""

jornada_auxiliares_padrao = """00:00 04:00 05:15 09:33 10
04:00 09:00 10:15 13:07 17
12:00 16:00 17:15 22:02 2
13:00 16:00 17:15 22:55 3
15:45 18:00 18:15 22:00 3
16:30 19:30 19:45 22:39 2
17:48 21:48 1
18:00 22:00 19
19:00 22:52 5"""

def ler_arquivo(f):
    if f:
        if f.name.endswith('.xlsx'):
            df = pd.read_excel(f, header=None)
            return '\n'.join(df.astype(str).apply(' '.join', axis=1))
        return f.getvalue().decode('utf-8')
    return None

jc = ler_arquivo(uploaded_conf) or jornada_conferentes_padrao
ja = ler_arquivo(uploaded_aux) or jornada_auxiliares_padrao

def ler_jornadas(t):
    j = []
    for l in t.strip().split('\n'):
        p = l.strip().split()
        if len(p) == 5 and p[4].isdigit():
            j.append({'tipo':'completa','entrada':p[0],'saida_intervalo':p[1],'retorno_intervalo':p[2],'saida_final':p[3],'quantidade':int(p[4])})
        elif len(p) == 3 and p[2].isdigit():
            j.append({'tipo':'meia','entrada':p[0],'saida_final':p[1],'quantidade':int(p[2])})
    return j

def coletar_horarios(jc, ja):
    h = set(['00:00','23:59'])
    for t in [jc, ja]:
        for l in t.strip().split('\n'):
            p = l.strip().split()
            if len(p) in (3,5):
                h.update(p[:-1])
    return sorted(h, key=lambda x: int(x.split(':')[0])*60 + int(x.split(':')[1]))

def hora_para_min(h):
    try: return int(h.split(':')[0])*60 + int(h.split(':')[1])
    except: return 0

def processar(jc, ja):
    horarios = coletar_horarios(jc, ja)
    timeline = [hora_para_min(h) for h in horarios]
    conf = [0]*len(timeline)
    aux = [0]*len(timeline)
    for j in ler_jornadas(jc):
        e = hora_para_min(j['entrada'])
        sf = hora_para_min(j['saida_final'])
        if j['tipo']=='completa':
            si = hora_para_min(j['saida_intervalo'])
            ri = hora_para_min(j['retorno_intervalo'])
            for i,t in enumerate(timeline):
                if (e<=t<si) or (ri<=t<=sf): conf[i] += j['quantidade']
        else:
            for i,t in enumerate(timeline):
                if e<=t<=sf: conf[i] += j['quantidade']
    for j in ler_jornadas(ja):
        e = hora_para_min(j['entrada'])
        sf = hora_para_min(j['saida_final'])
        if j['tipo']=='completa':
            si = hora_para_min(j['saida_intervalo'])
            ri = hora_para_min(j['retorno_intervalo'])
            for i,t in enumerate(timeline):
                if (e<=t<si) or (ri<=t<=sf): aux[i] += j['quantidade']
        else:
            for i,t in enumerate(timeline):
                if e<=t<=sf: aux[i] += j['quantidade']
    return pd.DataFrame({'Horário':horarios,'Conferentes':conf,'Auxiliares':aux})

df = processar(jc, ja)

col1, col2, col3 = st.columns([1,1,6])
with col1: rotulos = st.checkbox("Rótulos", True)
with col2: st.markdown("**Clique no gráfico para maximizar**")

output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as w:
    df.to_excel(w, index=False)
output.seek(0)
st.download_button("📥 Baixar Excel", output, "disponibilidade.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

fig = make_subplots()
fig.add_trace(go.Scatter(x=df['Horário'], y=df['Conferentes'], name='Conferentes', line=dict(color='#90EE90'), fill='tozeroy', fillcolor='rgba(144,238,144,0.3)'))
fig.add_trace(go.Scatter(x=df['Horário'], y=df['Auxiliares'], name='Auxiliares', line=dict(color='#228B22'), fill='tozeroy', fillcolor='rgba(34,139,34,0.3)'))
if '09:30' in df['Horário'].values:
    fig.add_vrect(x0='09:30', x1='10:30', fillcolor="gray", opacity=0.1)
if rotulos:
    for _, r in df.iterrows():
        if r['Conferentes']>0:
            fig.add_annotation(x=r['Horário'], y=r['Conferentes']+0.8, text=str(int(r['Conferentes'])), showarrow=False, font=dict(color='#90EE90'))
        if r['Auxiliares']>0:
            fig.add_annotation(x=r['Horário'], y=r['Auxiliares']+0.8, text=str(int(r['Auxiliares'])), showarrow=False, font=dict(color='#228B22'))
fig.update_layout(title="Disponibilidade de Equipe", xaxis_title="Horário", yaxis_title="Colaboradores", height=600, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.markdown("**Upload → Rótulos → Maximizar → Baixar Excel**")
