# pages/4_Producao_x_Equipe_V4.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(layout="wide", page_title="Produção vs Equipe - V4 Final")

# ==================== TÍTULO PRINCIPAL ====================
st.title("🚛 Produção vs Equipe + Janelas Críticas com Toneladas")
st.markdown("##### **Versão Final – V4 | Dados reais de operação incluídos | 27/11/2025**")
st.markdown("---")

# ==================== DADOS FIXOS (AGORA COM ENTREGA E COLETA REAIS) ====================
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

# <<< NOVOS DADOS FIXOS >>>
entrega_fixa = """07:40 3,0
08:00 7,0
08:10 9,0
08:20 10,0
08:20 12,2
09:00 15,2
14:00 8,6
14:00 7,5
14:00 7,0
14:20 3,0"""

coleta_fixa = """18:00 20,5
18:15 10,2
18:30 8,0
18:45 17,6
19:00 7,5
19:15 9,3
19:30 10,0"""

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

# ==================== PROCESSAMENTO (com valores padrão já carregados) ====================
with st.spinner("Gerando gráfico com dados reais..."):

    # Pega inputs do session_state (ou usa fixo se vazio)
    nova_chegada = st.session_state.get("nova_chegada", chegada_fixa)
    nova_saida = st.session_state.get("nova_saida", saida_fixa)
    entrega_input = st.session_state.get("entrega_input", entrega_fixa)
    coleta_input = st.session_state.get("coleta_input", coleta_fixa)
    nova_confer = st.session_state.get("nova_confer", confer_fixa)
    nova_aux = st.session_state.get("nova_aux", aux_fixa)

    # Usa os valores (fixos ou digitados)
    chegada_txt = nova_chegada.strip()
    saida_txt = nova_saida.strip()
    confer_txt = nova_confer.strip()
    aux_txt = nova_aux.strip()

    # === Processa Entrega e Coleta (agora com valores fixos fortes!) ===
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

    # === Funções de apoio ===
    def extrair_producao(chegada, saida):
        cheg = {}; said = {}
        for l in chegada.strip().split("\n"):
            p = l.strip().split()
            if len(p) >= 2:
                h, v = p[0], p[1]
                try: cheg[h] = cheg.get(h, 0) + float(v.replace(",", "."))
                except: pass
        for l in saida.strip().split("\n"):
            p = l.strip().split()
            if len(p) >= 2:
                h, v = p[0], p[1]
                try: said[h] = said.get(h, 0) + float(v.replace(",", "."))
                except: pass
        return cheg, said

    cheg, said = extrair_producao(chegada_txt, saida_txt)

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
                if len(p) >= 2:
                    h.add(p[0])
        return sorted(h, key=min_hora)

    # Monta lista completa de horários
    jornadas_conf = jornadas(confer_txt)
    jornadas_aux = jornadas(aux_txt)
    todas_horas = set(cheg) | set(said) | set(entrega_dict) | set(coleta_dict)
    todas_horas.update(get_horarios(confer_txt, aux_txt))
    horarios = sorted(todas_horas, key=min_hora)

    # Calcula equipe por horário
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
    eq_total = [a + b for a, b in zip(eq_conf, eq_aux)]

    # Monta DataFrame
    df = pd.DataFrame({
        "Horario": horarios,
        "Chegada_Ton": [round(cheg.get(h, 0), 1) for h in horarios],
        "Saida_Ton": [round(said.get(h, 0), 1) for h in horarios],
        "Entrega_Ton": [round(entrega_dict.get(h, 0), 1) for h in horarios],
        "Coleta_Ton": [round(coleta_dict.get(h, 0), 1) for h in horarios],
        "Equipe": eq_total
    })

    max_ton = max(df[["Chegada_Ton", "Saida_Ton", "Entrega_Ton", "Coleta_Ton"]].max()) + 10
    scale = max_ton / (df["Equipe"].max() + 5) if df["Equipe"].max() > 0 else 1
    df["Equipe_Escalada"] = df["Equipe"] * scale

    # ==================== GRÁFICO (AGORA COM ENTREGA E COLETA FORTES!) ====================
    rotulos = st.session_state.get("rotulos", True)
    mostrar_simbolos = st.session_state.get("mostrar_simbolos", True)

    fig = go.Figure()

    fig.add_trace(go.Bar(x=df["Horario"], y=df["Chegada_Ton"], name="Chegada Coleta", marker_color="#90EE90", opacity=0.85))
    fig.add_trace(go.Bar(x=df["Horario"], y=df["Saida_Ton"], name="Saída Linha (Cross)", marker_color="#E74C3C", opacity=0.85))
    fig.add_trace(go.Bar(x=df["Horario"], y=df["Entrega_Ton"], name="Saída para Entrega", marker_color="#3498DB", opacity=0.9))
    fig.add_trace(go.Bar(x=df["Horario"], y=df["Coleta_Ton"], name="Retorno de Coleta", marker_color="#E67E22", opacity=0.9))

    fig.add_trace(go.Scatter(
        x=df["Horario"], y=df["Equipe_Escalada"],
        mode="lines+markers+text",
        name="Equipe Disponível",
        line=dict(color="#9B59B6", width=5, dash="dot"),
        marker=dict(size=10),
        text=df["Equipe"],
        textposition="top center",
        textfont=dict(size=11, color="#9B59B6", family="Arial Black"),
        customdata=df["Equipe"],
        hovertemplate="Equipe: <b>%{customdata}</b> pessoas<extra></extra>"
    ))

    if mostrar_simbolos:
        # Triângulo azul pra cima = saída entrega
        entrega_hrs = [h for h, t in entrega_dict.items() if t > 0]
        if entrega_hrs:
            fig.add_trace(go.Scatter(x=entrega_hrs, y=[max_ton * 1.1] * len(entrega_hrs),
                                  mode="markers", marker=dict(color="#2980B9", size=26, symbol="triangle-up"),
                                  name="Saída Entrega", hoverinfo="skip")
        )
        # Triângulo laranja pra baixo = retorno coleta
        coleta_hrs = [h for h, t in coleta_dict.items() if t > 0]
        if coleta_hrs:
            fig.add_trace(go.Scatter(x=coleta_hrs, y=[max_ton * 1.1] * len(coleta_hrs),
                                     mode="markers", marker=dict(color="#D35400", size=26, symbol="triangle-down"),
                                     name="Retorno Coleta", hoverinfo="skip"))

    # Rótulos bonitões
    if rotulos:
        for _, r in df.iterrows():
            if r["Chegada_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Chegada_Ton"], text=f"+{r['Chegada_Ton']}", font=dict(color="#27AE60", size=10, weight="bold"), yshift=12, showarrow=False)
            if r["Saida_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Saida_Ton"], text=f"-{r['Saida_Ton']}", font=dict(color="#C0392B", size=10, weight="bold"), yshift=12, showarrow=False)
            if r["Entrega_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Entrega_Ton"], text=f"→{r['Entrega_Ton']}", font=dict(color="#2980B9", size=11, weight="bold"), yshift=12, showarrow=False)
            if r["Coleta_Ton"] > 0:
                fig.add_annotation(x=r["Horario"], y=r["Coleta_Ton"], text=f"←{r['Coleta_Ton']}", font=dict(color="#D35400", size=11, weight="bold"), yshift=12, showarrow=False)

    fig.update_layout(
        height=800,
        barmode="relative",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, x=0.),
        yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.3]),
        xaxis_title="Horário",
        margin=dict(t=80)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Download Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Operação Completa', index=False)
    buffer.seek(0)
    st.download_button("📊 Baixar dados em Excel", buffer, f"operacao_{pd.Timestamp('today').strftime('%d%m%Y')}.xlsx")

# ==================== INPUTS (só agora, lá embaixo) ====================
st.markdown("---")
st.markdown("### ✏️ Editar Dados (Opcional – substitui os valores padrão)")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### Chegadas (Coleta)")
    nova_chegada = st.text_area("", value=chegada_fixa, height=320, key="nova_chegada")
    st.markdown("#### Conferentes")
    nova_confer = st.text_area("", value=confer_fixa, height=320, key="nova_confer")

with col2:
    st.markdown("#### Saídas Linha (Cross-Docking)")
    nova_saida = st.text_area("", value=saida_fixa, height=320, key="nova_saida")
    st.markdown("#### Auxiliares / Movimentadores")
    nova_aux = st.text_area("", value=aux_fixa, height=320, key="nova_aux")

with col3:
    st.markdown("#### Saída para Entrega (caminhões locais)")
    entrega_input = st.text_area("", value=entrega_fixa, height=200, key="entrega_input")
    st.markdown("#### Retorno de Coleta")
    coleta_input = st.text_area("", value=coleta_fixa, height=200, key="coleta_input")
    st.markdown("#### Opções do Gráfico")
    st.checkbox("Mostrar rótulos", value=True, key="rotulos")
    st.checkbox("Mostrar triângulos de saída/retorno", value=True, key="mostrar_simbolos")

st.success("Dados reais de entrega e coleta já carregados! Gráfico atualiza em tempo real.")
