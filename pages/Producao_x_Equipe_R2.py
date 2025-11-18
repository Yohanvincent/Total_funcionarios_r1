# pages/3_Producao_x_Equipe.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io
from datetime import datetime

st.set_page_config(layout="wide", page_title="Produção x Equipe")
st.title("🚛 Produção vs Equipe Disponível - Cross-Docking Fracionado")

st.markdown("### Cole os dados abaixo para gerar o gráfico em tempo real")

# =============================================
# FUNÇÕES AUXILIARES
# =============================================
def min_hora(h):
    try:
        h = str(h).strip()
        if ":" not in h:
            return 0
        hh, mm = map(int, h.split(":"))
        return hh * 60 + mm
    except:
        return 0

def calcular_equipe_por_hora(jornadas, horarios_min):
    equipe = [0] * len(horarios_min)
    for j in jornadas:
        entrada = min_hora(j["entrada"])
        if j["tipo"] == "conferente":
            saida_int = min_hora(j["saida_int"])
            retorno_int = min_hora(j["retorno_int"])
            saida_final = min_hora(j["saida_final"])
            for i, t in enumerate(horarios_min):
                if (entrada <= t < saida_int) or (retorno_int <= t <= saida_final):
                    equipe[i] += j["qtd"]
        else:  # auxiliar
            saida = min_hora(j["saida"])
            for i, t in enumerate(horarios_min):
                if entrada <= t <= saida:
                    equipe[i] += j["qtd"]
    return equipe

# =============================================
# CAMPOS DE ENTRADA (COLAR DADOS)
# =============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Chegadas de Carga (toneladas)")
    chegadas_texto = st.text_area(
        "Cole aqui: Horário Toneladas (um por linha)",
        height=300,
        value="""04:00 5.2
04:30 15.8
05:00 12.4
05:00 8.7
05:30 9.1
06:00 14.3
10:00 3.0""",
        help="Ex: 05:00 15.5"
    )

    st.subheader("👥 Conferentes (jornada com intervalo)")
    conferentes_texto = st.text_area(
        "Cole aqui: Entrada Saída_Int Retorno_Int Saída_Final Qtd",
        height=250,
        value="""04:30 09:30 10:30 13:26 2
16:00 20:00 21:00 01:24 3
18:30 22:30 23:30 03:38 4
19:00 23:00 00:05 04:09 8
21:00 01:00 02:05 06:08 5
22:00 02:00 03:05 07:03 9
23:30 03:30 04:35 08:49 19""",
        help="Ex: 04:30 09:30 10:30 13:26 2 → 2 conferentes nesse horário"
    )

with col2:
    st.subheader("📤 Saídas de Carga (toneladas)")
    saidas_texto = st.text_area(
        "Cole aqui: Horário Toneladas (um por linha)",
        height=300,
        value="""05:00 15.7
06:00 14.4
06:00 10.4
07:00 15.9
07:00 13.1
21:30 14.6
22:30 17.2
23:00 8.5""",
        help="Ex: 07:00 18.9"
    )

    st.subheader("🧑‍🔧 Auxiliares (jornada simples)")
    auxiliares_texto = st.text_area(
        "Cole aqui: Entrada Saída Qtd",
        height=250,
        value="""16:00 01:24 5
18:00 03:12 1
19:00 04:09 13
21:00 06:08 29
22:00 07:03 20
23:30 08:49 25""",
        help="Ex: 19:00 04:09 12 → 12 auxiliares trabalhando até 04:09"
    )

rotulos = st.checkbox("Exibir rótulos nos gráficos", value=True)

# =============================================
# PROCESSAMENTO DOS DADOS
# =============================================
try:
    # --- Chegadas ---
    chegadas = {}
    for linha in chegadas_texto.strip().split("\n"):
        if not linha.strip(): continue
        partes = linha.strip().split()
        if len(partes) >= 2:
            hora = partes[0]
            try:
                ton = float(partes[1].replace(",", "."))
                chegadas[hora] = chegadas.get(hora, 0) + ton
            except:
                pass

    # --- Saídas ---
    saidas = {}
    for linha in saidas_texto.strip().split("\n"):
        if not linha.strip(): continue
        partes = linha.strip().split()
        if len(partes) >= 2:
            hora = partes[0]
            try:
                ton = float(partes[1].replace(",", "."))
                saidas[hora] = saidas.get(hora, 0) + ton
            except:
                pass

    # --- Jornadas Conferentes ---
    jornadas_conferentes = []
    for linha in conferentes_texto.strip().split("\n"):
        partes = linha.strip().split()
        if len(partes) == 5 and partes[4].isdigit():
            jornadas_conferentes.append({
                "tipo": "conferente",
                "entrada": partes[0],
                "saida_int": partes[1],
                "retorno_int": partes[2],
                "saida_final": partes[3],
                "qtd": int(partes[4])
            })

    # --- Jornadas Auxiliares ---
    jornadas_auxiliares = []
    for linha in auxiliares_texto.strip().split("\n"):
        partes = linha.strip().split()
        if len(partes) == 3 and partes[2].isdigit():
            jornadas_auxiliares.append({
                "tipo": "auxiliar",
                "entrada": partes[0],
                "saida": partes[1],
                "qtd": int(partes[2])
            })

    # Todos os horários únicos
    todos_horarios = set(chegadas.keys()) | set(saidas.keys())
    for j in jornadas_conferentes + jornadas_auxiliares:
        todos_horarios.add(j["entrada"])
        if j["tipo"] == "conferente":
            todos_horarios.update([j["saida_int"], j["retorno_int"], j["saida_final"]])
        else:
            todos_horarios.add(j["saida"])

    horarios = sorted(todos_horarios, key=min_hora)
    horarios_min = [min_hora(h) for h in horarios]

    # Calcular equipe por horário
    equipe_conf = calcular_equipe_por_hora(jornadas_conferentes, horarios_min)
    equipe_aux = calcular_equipe_por_hora(jornadas_auxiliares, horarios_min)
    equipe_total = [c + a for c, a in zip(equipe_conf, equipe_aux)]

    # DataFrame final
    df = pd.DataFrame({
        "Horário": horarios,
        "Chegada (ton)": [round(chegadas.get(h, 0), 1) for h in horarios],
        "Saída (ton)": [round(saidas.get(h, 0), 1) for h in horarios],
        "Conferentes": equipe_conf,
        "Auxiliares": equipe_aux,
        "Equipe Total": equipe_total
    })

    # Escala da equipe
    max_ton = max(df["Chegada (ton)"].max(), df["Saída (ton)"].max(), 1)
    max_eq = df["Equipe Total"].max() or 1
    escala = max_ton / (max_eq + 2)
    df["Equipe Esculada"] = df["Equipe Total"] * escala

    # =============================================
    # GRÁFICO
    # =============================================
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["Horário"], y=df["Chegada (ton)"],
        name="Chegada", marker_color="#2ECC71", opacity=0.85
    ))
    fig.add_trace(go.Bar(
        x=df["Horário"], y=df["Saída (ton)"],
        name="Saída", marker_color="#E74C3C", opacity=0.85
    ))
    fig.add_trace(go.Scatter(
        x=df["Horário"], y=df["Equipe Esculada"],
        mode="lines+markers+text",
        name="Equipe Disponível",
        line=dict(color="#9B59B6", width=5, dash="solid"),
        marker=dict(size=10),
        text=df["Equipe Total"],
        textposition="top center",
        textfont=dict(size=12, color="#8E44AD", family="Arial Black"),
        hovertemplate="<b>%{x}</b><br>Equipe: <b>%{text}</b> pessoas<extra></extra>"
    ))

    if rotulos:
        for _, r in df.iterrows():
            if r["Chegada (ton)"] > 0:
                fig.add_annotation(x=r["Horário"], y=r["Chegada (ton)"], text=str(r["Chegada (ton)"]),
                                   font=dict(color="darkgreen", size=10), showarrow=False, yshift=10)
            if r["Saída (ton)"] > 0:
                fig.add_annotation(x=r["Horário"], y=r["Saída (ton)"], text=str(r["Saída (ton)"]),
                                   font=dict(color="darkred", size=10), showarrow=False, yshift=10)

    fig.update_layout(
        title="Produção × Equipe Disponível (Cross-Docking)",
        xaxis_title="Horário",
        yaxis_title="Toneladas | Equipe (escalada)",
        height=700,
        barmode="stack",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100)
    )

    st.plotly_chart(fig, use_container_width=True)

    # =============================================
    # RESUMO E DOWNLOAD
    # =============================================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Chegada", f"{df['Chegada (ton)'].sum():.1f} ton")
    col2.metric("Total Saída", f"{df['Saída (ton)'].sum():.1f} ton")
    col3.metric("Pico de Equipe", f"{df['Equipe Total'].max()} pessoas")
    col4.metric("Média Equipe", f"{df['Equipe Total'].mean():.1f} pessoas")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Relatório", index=False)
    buffer.seek(0)

    st.download_button(
        "📥 Baixar Relatório Completo (Excel)",
        data=buffer,
        file_name=f"producao_equipe_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("✅ Gráfico atualizado com sucesso!")

except Exception as e:
    st.error(f"Erro ao processar os dados. Verifique o formato e tente novamente.\nDetalhe: {str(e)}")
