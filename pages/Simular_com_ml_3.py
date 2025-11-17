import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Logística - Análise Semanal", layout="wide")
st.title("Análise e Previsão de Acúmulo de Carga - Segunda a Sexta")

st.markdown("""
### Qual é o objetivo deste painel?
Este aplicativo simula **exatamente o que acontece no pátio e no cross-docking da sua agência todos os dias úteis**, hora a hora, e usa **Machine Learning** para prever o acúmulo futuro de carga.

Você vai conseguir responder perguntas reais do dia a dia:
- Quantas toneladas vão estar acumuladas na quarta-feira às 08:00?
- Se eu colocar +1 auxiliar na quinta, o pico diminui quanto?
- Qual é o dia mais crítico da semana?
- Quantas pessoas preciso no mínimo para não deixar passar de 20 ton no pátio?
""")

# ==================== UPLOAD DO ARQUIVO ====================
uploaded_file = st.file_uploader(
    "Faça upload do seu CSV com os dados da semana (segunda a sexta)",
    type=["csv"],
    help="Colunas obrigatórias: Data (ex: 2025-11-10), Hora (ex: 05:00), Chegada_Ton, Saida_Priorizada, Equipe_Disponivel"
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # ==================== TRATAMENTO DOS DADOS ====================
    df["Data"] = pd.to_datetime(df["Data"])
    df = df[df["Data"].dt.weekday < 5].copy()  # FILTRA APENAS SEGUNDA A SEXTA
    df["Dia_semana"] = df["Data"].dt.day_name(locale='pt_BR').str[:3]  # Seg, Ter, Qua...
    df["Datetime"] = df["Data"] + pd.to_timedelta(df["Hora"] + ":00")
    df = df.sort_values("Datetime").reset_index(drop=True)

    # Cálculos importantes
    df["Capacidade_ton_hora"] = df["Equipe_Disponivel"] * (3600 / 34)  # 34 segundos médio por operação
    df["Acumulacao"] = (df["Chegada_Ton"].cumsum() - df["Saida_Priorizada"].cumsum()).clip(lower=0)

    st.success(f"Carregados {len(df['Data'].dt.date.unique())} dias úteis: "
               f"{df['Data'].min().strftime('%d/%m')} → {df['Data'].max().strftime('%d/%m')}")

    # ==================== MÉTRICAS PRINCIPAIS ====================
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total de carga chegada na semana", f"{df['Chegada_Ton'].sum():.0f} ton")
    with col2: st.metric("Total de carga expedida", f"{df['Saida_Priorizada'].sum():.0f} ton")
    with col3: st.metric("Pico máximo da semana", f"{df['Acumulacao'].max():.0f} ton", delta=None)
    with col4: st.metric("Média do pico diário", f"{df.groupby(df['Data'].dt.date)['Acumulacao'].max().mean():.1f} ton")
    with col5: st.metric("Dia mais crítico", df.loc[df['Acumulacao'].idxmax(), 'Data'].strftime('%a %d/%m'))

    # ==================== GRÁFICO DA SEMANA INTEIRA ====================
    st.subheader("Acumulação de carga durante toda a semana útil")
    fig_semana = px.line(df, x="Datetime", y="Acumulacao", color="Dia_semana",
                         title="Evolução do acúmulo no pátio - Segunda a Sexta",
                         labels={"Acumulacao": "Acúmulo no pátio (toneladas)", "Datetime": "Data e Hora"},
                         markers=False, height=600)
    fig_semana.update_layout(legend_title="Dia da semana", hovermode="x unified")
    st.plotly_chart(fig_semana, use_container_width=True)

    # ==================== GRÁFICO POR DIA DA SEMANA (MÉDIA) ====================
    st.subheader("Perfil médio de acúmulo por dia da semana")
    df_media = df.groupby(["Dia_semana", df["Datetime"].dt.hour])["Acumulacao"].mean().reset_index()
    df_media["Hora"] = df_media["Datetime"].apply(lambda x: f"{x:02d}:00")
    ordem_dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    fig_media = px.line(df_media, x="Hora", y="Acumulacao", color="Dia_semana",
                        category_orders={"Dia_semana": ordem_dias},
                        title="Padrão médio de acúmulo por dia útil",
                        labels={"Acumulacao": "Acúmulo médio (ton)"},
                        markers=True)
    st.plotly_chart(fig_media, use_container_width=True)

    # ==================== MACHINE LEARNING - PREVISÃO ====================
    st.subheader("Previsão com Machine Learning (Random Forest)")

    df_ml = df.copy()
    df_ml["Dia_da_semana_num"] = df_ml["Data"].dt.weekday  # 0=Seg, 4=Sex
    df_ml["Minutos_do_dia"] = df_ml["Datetime"].dt.hour * 60 + df_ml["Datetime"].dt.minute

    X = df_ml[["Dia_da_semana_num", "Minutos_do_dia", "Chegada_Ton", "Equipe_Disponivel"]]
    y = df_ml["Acumulacao"]

    modelo = RandomForestRegressor(n_estimators=200, random_state=42)
    modelo.fit(X, y)

    st.success("Modelo treinado com todos os dias úteis carregados!")

    # ==================== SIMULADOR "E SE..." ====================
    st.subheader("Simulador: 'E se eu mudar a equipe?'")
    dia_escolhido = st.selectbox("Escolha o dia da semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"])
    equipe_nova = st.slider("Quantas pessoas trabalhando nesse dia?", 1, 6, 2)

    mapa_dia = {"Segunda":0, "Terça":1, "Quarta":2, "Quinta":3, "Sexta":4}
    dia_num = mapa_dia[dia_escolhido]

    previsoes = []
    for hora in range(0, 24):
        for minuto in [0, 30]:
            minutos = hora * 60 + minuto
            # Usa a média histórica de chegada naquele horário e dia da semana
            chegada_media = df[(df["Data"].dt.weekday == dia_num) & 
                              (df["Datetime"].dt.hour == hora)]["Chegada_Ton"].mean()
            if pd.isna(chegada_media): chegada_media = 0

            pred = modelo.predict([[dia_num, minutos, chegada_media, equipe_nova]])[0]
            previsoes.append({"Hora": f"{hora:02d}:{minuto:02d}", "Acumulo_Previsto": max(0, round(pred, 1))})

    df_simulacao = pd.DataFrame(previsoes)
    fig_sim = px.line(df_simulacao, x="Hora", y="Acumulo_Previsto",
                      title=f"Previsão de acúmulo - {dia_escolhido} com {equipe_nova} pessoas",
                      labels={"Acumulo_Previsto": "Acúmulo previsto (ton)"}, markers=True)
    fig_sim.add_hline(y=20, line_dash="dash", line_color="red", 
                      annotation_text="Limite crítico 20 ton")
    st.plotly_chart(fig_sim, use_container_width=True)

    pico = df_simulacao["Acumulo_Previsto"].max()
    st.write(f"**Pico previsto:** {pico} toneladas")
    if pico <= 15:
        st.success("Excelente! Operação tranquila com essa equipe.")
    elif pico <= 25:
        st.warning("Atenção: pico elevado, mas ainda gerenciável.")
    else:
        st.error("Alerta: risco de gargalo grave! Considere mais equipe ou ajustar saídas.")

else:
    st.info("Aguardando upload do arquivo CSV com os dias úteis...")
    csv_exemplo = """Data,Hora,Chegada_Ton,Saida_Priorizada,Equipe_Disponivel
2025-11-10,04:00,6,0,2
2025-11-10,05:00,18,0,2
2025-11-10,06:00,0,12,2
2025-11-11,04:00,5,0,2
2025-11-11,05:00,14,0,2
2025-11-12,05:00,20,0,2
2025-11-13,05:00,16,0,2
2025-11-14,05:00,22,0,3"""
    st.download_button("Baixar exemplo (segunda a sexta)", csv_exemplo, "dados_semana_util.csv", "text/csv")

st.caption("Desenvolvido para transportadoras de carga fracionada | Tempo médio por operação: 34 segundos | Modelo: Random Forest")
