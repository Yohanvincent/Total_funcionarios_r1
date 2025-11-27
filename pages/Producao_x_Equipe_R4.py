# pages/4_Producao_x_Equipe_V4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(layout="wide", page_title="Produção vs Equipe - V4 Final")

# ==================== TÍTULO PRINCIPAL (LOGO NO TOPO) ====================
st.title("🚛 Produção vs Equipe + Janelas Críticas com Toneladas")
st.markdown("##### **Versão Final – V4 | Atualizada em 27/11/2025**")
st.markdown("---")

# ==================== DADOS FIXOS (mantidos) ====================
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

# ==================== INPUTS VÃO FICAR AQUI EMBAIXO, SÓ DEPOIS DO GRÁFICO ===

# ==================== PLACEHOLDERS PARA INPUTS (vão ser preenchidos depois) ====================
ph_inputs = st.empty()

# ==================== PROCESSAMENTO DOS DADOS (executa com valores padrão primeiro) ====================
with st.spinner("Calculando produção e equipe..."):
    # Captura os inputs (inicialmente vazios = usa fixos)
    nova_chegada = st.session_state.get("nova_chegada", "")
    nova_saida = st.session_state.get("nova_saida", "")
    nova_confer = st.session_state.get("nova_confer", "")
    nova_aux = st.session_state.get("nova_aux", "")
    entrega_input = st.session_state.get("entrega_input", "")
    coleta_input = st.session_state.get("coleta_input", "")

    chegada_txt = nova_chegada.strip() if nova_chegada.strip() else chegada_fixa
    saida_txt = nova_saida.strip() if nova_saida.strip() else saida_fixa
    confer_txt = nova_confer.strip() if nova_confer.strip() else confer_fixa
    aux_txt = nova_aux.strip() if nova_aux.strip() else aux_fixa

    # Processa entregas e coletas
    entrega_dict = {}
    for linha in entrega_input.strip().split("\n"):
        if not linha.strip(): continue
        partes = linha.strip().split()
        if len(partes) >= 2:
            hora = partes[0]
            try:
                ton = float(partes[1].replace(",", "."))
                entrega_dict[hora] = entrega_dict.get(hora, 0) + ton
            except: pass

    coleta_dict = {}
    for linha in coleta_input.strip().split("\n"):
        if not linha.strip(): continue
        partes = linha.strip().split()
        if len(partes) >= 2:
            hora = partes[0]
            try:
                ton = float(partes[1].replace(",", "."))
                coleta_dict[hora] = coleta_dict.get(hora, 0) + ton
            except: pass

    # Funções de extração e jornada (mantidas 100%)
    def extrair_producao(texto):
        cheg = {}; said = {}
        modo = None
        for l in texto.strip().split("\n"):
            l = l.strip()
            if l == "Cheg. Ton.": modo = "cheg"; continue
            if l == "Saida Ton.": modo = "said"; continue
            if not l or modo is None: continue
            p = l.split()
            if len(p) < 2: continue
            h = p[0]
            try:
                v = float(p[1].replace(",", "."))
                if modo == "cheg": cheg[h] = cheg.get(h, 0) + v
                else: said[h] = said.get(h, 0) + v
            except: pass
        return cheg, said

    cheg, said = extrair_producao(f"Cheg. Ton.\n{chegada_txt}\nSaida Ton.\n{saida_txt}")

    def jornadas(t):
        j = []
        for l in t.strip().split("\n"):
            p = l.strip().split()
            if not p: continue
            if len(p) == 5 and p[4].isdigit():
                j.append({"t": "c", "e": p[0], "si": p[1], "ri": p[2], "sf": p[3], "q": int(p[4])})
            elif len(p) == 3 and p[2].isdigit():
                j.append({"t": "m", "e": p[0], "sf": p[1], "q": int(p[2])})
        return j

    def min_hora(h):
        try: hh, mm = map(int, h.split(":")); return hh*60 + mm
        except: return 0

    def get_horarios(*texts):
        h = set()
        for t in texts:
            for l in t.strip().split("\n"):
                p = l.strip().split()
                if len(p) in (3, 5):
                    h.update(p[:-1])
        return sorted(h, key=min_hora)

    jornadas_conf = jornadas(confer_txt)
    jornadas_aux = jornadas(aux_txt)
    todas_horas = set(cheg) | set(said) | set(entrega_dict) | set(coleta_dict)
    horas_equipe = get_horarios(confer_txt, aux_txt)
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

    eq_total = [a + b for a, b in zip(calcular_equipe(jornadas_conf, horarios), calcular_equipe(jornadas_aux, horarios))]

    cheg_val = [round(cheg.get(h, 0), 1) for h in horarios]
    said_val = [round(said.get(h, 0), 1) for h in horarios]
    entrega_val = [round(entrega_dict.get(h, 0), 1) for h in horarios]
    coleta_val = [round(coleta_dict.get(h, 0), 1) for h in horarios]

    df = pd.DataFrame({
        "Horario": horarios,
        "Chegada_Ton": cheg_val,
        "Saida_Ton": said_val,
        "Entrega_Ton": entrega_val,
        "Coleta_Ton": coleta_val,
        "Equipe": eq_total
    })

    max_ton = max(max(cheg_val), max(said_val), max(entrega_val), max(coleta_val), 10) + 10
    scale = max_ton / (max(eq_total) + 5) if max(eq_total) > 0 else 1
    df["Equipe_Escalada"] = df["Equipe"] * scale

    # ==================== GRÁFICO (AGORA APARECE PRIMEIRO!) ====================
    rotulos = st.session_state.get("rotulos", True)
    mostrar_simbolos = st.session_state.get("mostrar_simbolos", True)

    fig = go.Figure()

    fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada", marker_color="#90EE90", opacity=0.8))
    fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Carregada", marker_color="#E74C3C", opacity=0.8))
    fig.add_trace(go.Bar(x=df["Horario"], y=df["Entrega_Ton"], name="Saída para Entrega", marker_color="#3498DB", opacity=0.9))
    fig.add_trace(go.Bar(x=df["Horario"], y=df["Coleta_Ton"], name="Retorno de Coleta", marker_color="#E67E22", opacity=0.9))

    fig.add_trace(go.Scatter(
        x=df["Horario"], y=df["Equipe_Escalada"],
        mode="lines+markers", name="Equipe Disponível",
        line=dict(color="#9B59B6", width=5, dash="dot"),
        marker=dict(size=10),
        customdata=df["Equipe"],
        hovertemplate="Equipe: %{customdata} pessoas<extra></extra>"
    ))

    if mostrar_simbolos:
        entrega_hrs = [h for h, t in entrega_dict.items() if t > 0]
        if entrega_hrs:
            fig.add_trace(go.Scatter(x=entrega_hrs, y=[max_ton * 1.08] * len(entrega_hrs),
                                     mode="markers", marker=dict(color="#2980B9", size=24, symbol="triangle-up"),
                                     name="Saída Entrega", hoverinfo="skip"))
        coleta_hrs = [h for h, t in coleta_dict.items() if t > 0]
        if coleta_hrs:
            fig.add_trace(go.Scatter(x=coleta_hrs, y=[max_ton * 1.08] * len(coleta_hrs),
                                     mode="markers", marker=dict(color="#E67E22", size=24, symbol="triangle-down"),
                                     name="Retorno Coleta", hoverinfo="skip"))

    if rotulos:
        for _, r in df.iterrows():
            if r["Chegada_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"+{r['Chegada_Ton']}",
                                   font=dict(color="#2ECC71", size=10, weight="bold"), showarrow=False, yshift=12)
            if r["Saida_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"-{r['Saida_Ton']}",
                                   font=dict(color="#E74C3C", size=10, weight="bold"), showarrow=False, yshift=12)
            if r["Entrega_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Entrega_Ton"], text=f"{r['Entrega_Ton']}",
                                   font=dict(color="#2980B9", size=10, weight="bold"), showarrow=False, yshift=12)
            if r["Coleta_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Coleta_Ton"], text=f"{r['Coleta_Ton']}",
                                   font=dict(color="#D35400", size=10, weight="bold"), showarrow=False, yshift=12)
            if r["Equipe"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Equipe_Escalada"],
                                   text=f"{int(r['Equipe'])}",
                                   font=dict(color="#9B59B6", size=11, weight="bold"), bgcolor="white",
                                   bordercolor="#9B59B6", borderwidth=2, showarrow=False, yshift=8)

    fig.update_layout(
        title="",
        xaxis_title="Horário do Dia",
        yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.25]),
        height=800,
        barmode="relative",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=80)
    )

    # ==================== EXIBE O GRÁFICO LOGO NO TOPO ====================
    st.plotly_chart(fig, use_container_width=True)

    # ==================== DOWNLOAD DO EXCEL ====================
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Produção x Equipe', index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 Baixar dados em Excel",
        data=buffer,
        file_name=f"producao_equipe_{pd.Timestamp('today').strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==================== AGORA SIM: INPUTS ABAIXO DO GRÁFICO ====================
st.markdown("---")
st.markdown("### ✏️ Configuração dos Dados (Opcional – substitui os valores padrão)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Chegadas (horário + ton)")
    nova_chegada = st.text_area("Chegadas", value=chegada_fixa, height=300, key="nova_chegada")
    st.markdown("#### Conferentes (jornada)")
    nova_confer = st.text_area("Conferentes", value=confer_fixa, height=300, key="nova_confer")

with col2:
    st.markdown("#### Saídas Carregamento (horário + ton)")
    nova_saida = st.text_area("Saídas", value=saida_fixa, height=300, key="nova_saida")
    st.markdown("#### Auxiliares / Movimentadores")
    nova_aux = st.text_area("Auxiliares", value=aux_fixa, height=300, key="nova_aux")

with col3:
    st.markdown("#### Saída para Entrega (caminhões de entrega)")
    entrega_input = st.text_area("Ex: 08:00 14.5\n09:30 22.1", height=150, key="entrega_input")
    st.markdown("#### Retorno de Coleta")
    coleta_input = st.text_area("Ex: 18:00 12.8\n19:30 18.2", height=150, key="coleta_input")

    st.markdown("#### Opções do Gráfico")
    rotulos = st.checkbox("Mostrar rótulos de tonelada", value=True, key="rotulos")
    mostrar_simbolos = st.checkbox("Mostrar triângulos de saída/retorno", value=True, key="mostrar_simbolos")

st.info("⚡ Alterou algum dado? O gráfico atualiza automaticamente!")

# Força reexecução ao mudar inputs
st.rerun()
