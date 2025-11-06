# pages/2_Total_Funcionarios.py (MESMA LÓGICA DO GRÁFICO CONFERENTES VS AUXILIARES)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io

st.set_page_config(layout="wide")

st.title("Disponibilidade Total de Funcionários")
st.markdown("**Upload (Excel/CSV/TXT) ou use padrão.**")

c1, c2 = st.columns(2)
with c1: up_conf = st.file_uploader("Conferentes", ["txt","csv","xlsx"], key="tc")
with c2: up_aux = st.file_uploader("Auxiliares", ["txt","csv","xlsx"], key="ta")

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
        return pd.read_excel(f, header=None).apply(' '.join', axis=1).str.cat(sep='\n') if f.name.endswith('.xlsx') else f.getvalue().decode()
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
    try: h,m = map(int, h.split(':')); return h*60 + m
    except: return 0

def horarios(jc, ja):
    h = {'00:00','23:59'}
    for t in [jc, ja]:
        for l in t.split('\n'):
            p = l.strip().split()
            if len(p) in (3,5): h.update(p[:-1])
    return sorted(h, key=hor)

hs = horarios(jc, ja)
tl_min = [hor(h) for h in hs]  # timeline em minutos
total = [0]*len(tl_min)

def proc(j, lst, tl):
    e = hor(j['e'])
    sf = hor(j['sf'])
    if j['tipo']=='c':
        si = hor(j['si'])
        ri = hor(j['ri'])
        for i,t in enumerate(tl):
            if (e<=t<si) or (ri<=t<=sf): lst[i] += j['q']
    else:
        for i,t in enumerate(tl):
            if e<=t<=sf: lst[i] += j['q']

for j in jornadas(jc): proc(j, total, tl_min)
for j in jornadas(ja): proc(j, total, tl_min)

# --- DataFrame com horários originais ---
df = pd.DataFrame({
    'Horário': hs,
    'Total': total
})

c1, c2, _ = st.columns([1,1,6])
with c1: rot = st.checkbox("Rótulos", True, key="rt")
with c2: st.markdown("**Clique no gráfico para maximizar**")

out = io.BytesIO()
with pd.ExcelWriter(out, engine='openpyxl') as w: df.to_excel(w, index=False)
out.seek(0)
st.download_button("📥 Baixar Excel", out, "total.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df['Horário'], y=df['Total'],
    mode='lines+markers',
    name='Total',
    line=dict(color='#90EE90', width=4),
    marker=dict(size=6),
    fill='tozeroy',
    fillcolor='rgba(144,238,144,0.3)'
))

# Intervalo de almoço (se existir 09:30 e 10:30)
if '09:30' in df['Horário'].values and '10:30' in df['Horário'].values:
    fig.add_vrect(x0='09:30', x1='10:30', fillcolor="gray", opacity=0.1)

if rot:
    for _, r in df.iterrows():
        if r['Total'] > 0:
            fig.add_annotation(
                x=r['Horário'], y=r['Total']+0.8,
                text=str(int(r['Total'])),
                showarrow=False,
                font=dict(color='#90EE90', size=10, family="bold"),
                bgcolor="white", bordercolor='#90EE90', borderwidth=1, borderpad=4
            )

fig.update_layout(
    title="Total de Funcionários (mesma lógica do gráfico Conferentes vs Auxiliares)",
    xaxis_title="Horário",
    yaxis_title="Total",
    height=600,
    hovermode="x unified",
    margin=dict(l=40, r=40, t=80, b=40)
)

st.plotly_chart(fig, use_container_width=True)
