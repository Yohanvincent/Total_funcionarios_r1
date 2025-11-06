# pages/1_Conferentes_vs_Auxiliares.py (ATUALIZADO PARA LARGURA TOTAL)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

st.set_page_config(layout="wide")  # <-- FORÇA LARGURA TOTAL

st.title("Disponibilidade: Conferentes vs Auxiliares")
st.markdown("**Upload (Excel/CSV/TXT) ou use padrão.**")

c1, c2 = st.columns(2)
with c1: up_conf = st.file_uploader("Conferentes", ["txt","csv","xlsx"], key="c")
with c2: up_aux = st.file_uploader("Auxiliares", ["txt","csv","xlsx"], key="a")

padrao_conf = """00:00 04:00 05:15 09:33 9
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

padrao_aux = """00:00 04:00 05:15 09:33 10
04:00 09:00 10:15 13:07 17
12:00 16:00 17:15 22:02 2
13:00 16:00 17:15 22:55 3
15:45 18:00 18:15 22:00 3
16:30 19:30 19:45 22:39 2
17:48 21:48 1
18:00 22:00 19
19:00 22:52 5"""

def ler(f):
    if f:
        return pd.read_excel(f, header=None).apply(' '.join, axis=1).str.cat(sep='\n') if f.name.endswith('.xlsx') else f.getvalue().decode()
    return None

jc = ler(up_conf) or padrao_conf
ja = ler(up_aux) or padrao_aux

def jornadas(t):
    j = []
    for l in t.split('\n'):
        p = l.strip().split()
        if len(p)==5 and p[4].isdigit(): j.append({'tipo':'c','e':p[0],'si':p[1],'ri':p[2],'sf':p[3],'q':int(p[4])})
        if len(p)==3 and p[2].isdigit(): j.append({'tipo':'m','e':p[0],'sf':p[1],'q':int(p[2])})
    return j

def hor(h): 
    try: return int(h.split(':')[0])*60 + int(h.split(':')[1])
    except: return 0

def horarios(jc, ja):
    h = {'00:00','23:59'}
    for t in [jc, ja]:
        for l in t.split('\n'):
            p = l.strip().split()
            if len(p) in (3,5): h.update(p[:-1])
    return sorted(h, key=hor)

def processar(jc, ja):
    hs = horarios(jc, ja)
    tl = [hor(h) for h in hs]
    conf = [0]*len(tl)
    aux = [0]*len(tl)
    for j in jornadas(jc):
        e, sf = hor(j['e']), hor(j['sf'])
        if j['tipo']=='c':
            si, ri = hor(j['si']), hor(j['ri'])
            for i,t in enumerate(tl):
                if (e<=t<si) or (ri<=t<=sf): conf[i] += j['q']
        else:
            for i,t in enumerate(tl):
                if e<=t<=sf: conf[i] += j['q']
    for j in jornadas(ja):
        e, sf = hor(j['e']), hor(j['sf'])
        if j['tipo']=='c':
            si, ri = hor(j['si']), hor(j['ri'])
            for i,t in enumerate(tl):
                if (e<=t<si) or (ri<=t<=sf): aux[i] += j['q']
        else:
            for i,t in enumerate(tl):
                if e<=t<=sf: aux[i] += j['q']
    return pd.DataFrame({'Horário':hs, 'Conferentes':conf, 'Auxiliares':aux})

df = processar(jc, ja)

c1, c2, _ = st.columns([1,1,6])
with c1: rot = st.checkbox("Rótulos", True)
with c2: st.markdown("**Clique no gráfico para maximizar**")

out = io.BytesIO()
with pd.ExcelWriter(out, engine='openpyxl') as w: df.to_excel(w, index=False)
out.seek(0)
st.download_button("📥 Baixar Excel", out, "equipe.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

fig = make_subplots()
fig.add_trace(go.Scatter(x=df['Horário'], y=df['Conferentes'], name='Conferentes', line=dict(color='#90EE90'), fill='tozeroy', fillcolor='rgba(144,238,144,0.3)'))
fig.add_trace(go.Scatter(x=df['Horário'], y=df['Auxiliares'], name='Auxiliares', line=dict(color='#228B22'), fill='tozeroy', fillcolor='rgba(34,139,34,0.3)'))
if '09:30' in df['Horário'].values: fig.add_vrect(x0='09:30', x1='10:30', fillcolor="gray", opacity=0.1)
if rot:
    for _, r in df.iterrows():
        if r['Conferentes']>0: fig.add_annotation(x=r['Horário'], y=r['Conferentes']+0.8, text=str(int(r['Conferentes'])), showarrow=False, font=dict(color='#90EE90'))
        if r['Auxiliares']>0: fig.add_annotation(x=r['Horário'], y=r['Auxiliares']+0.8, text=str(int(r['Auxiliares'])), showarrow=False, font=dict(color='#228B22'))
fig.update_layout(
    title="Disponibilidade de Equipe",
    xaxis_title="Horário",
    yaxis_title="Pessoas",
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=80, b=40)  # <-- AJUSTE DE MARGENS
)

st.plotly_chart(fig, use_container_width=True)  # <-- LARGURA TOTAL
