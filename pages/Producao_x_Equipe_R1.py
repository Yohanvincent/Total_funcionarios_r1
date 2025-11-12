import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, time
import plotly.io as pio

# Configuração da página
st.set_page_config(page_title="App Logística - Capacidade Operacional", layout="wide")

# Função para converter hora string para datetime (assumindo data fixa, e.g., hoje)
def hora_to_datetime(hora_str, data_base='2025-11-12'):
    try:
        h = datetime.strptime(hora_str, '%H:%M').time()
        return datetime.combine(datetime.strptime(data_base, '%Y-%m-%d').date(), h)
    except:
        return None

# Dados de exemplo baseados no prompt (jornadas, chegadas de carga, saídas)
# Jornada exemplo: 04:30 - 09:30 (intervalo), 10:30 - 13:26, com 2 pessoas
jornadas = {
    'Jornada 1': {
        'entrada': '04:30',
        'fim_manha': '09:30',
        'inicio_tarde': '10:30',
        'saida': '13:26',
        'quantidade_pessoas': 2,
        'tipo': 'conferentes'  # ou 'auxiliares', etc.
    }
    # Pode adicionar mais jornadas
}

# Chegadas de carga exemplo
chegadas = [
    {'hora': '05:00', 'toneladas': 15},
    {'hora': '04:00', 'toneladas': 5},
    {'hora': '10:00', 'toneladas': 3},
    # Adicione mais
]

# Saídas prioritárias exemplo
saidas = [
    {'hora': '07:00', 'prioridade': 'alta', 'carga': 10},
    {'hora': '12:00', 'prioridade': 'media', 'carga': 8},
]

# Tempos de ciclo
TEMPO_DESCARGA_SEG = 30  # s por unidade (assumir por tonelada ou peça? Ajustar conforme)
TEMPO_CARGA_SEG = 38

# Função para calcular disponibilidade da equipe por hora
@st.cache_data
def calcular_disponibilidade_equipe(jornadas):
    df_disp = pd.DataFrame()
    for nome, dados in jornadas.items():
        entrada = hora_to_datetime(dados['entrada'])
        fim_manha = hora_to_datetime(dados['fim_manha'])
        inicio_tarde = hora_to_datetime(dados['inicio_tarde'])
        saida = hora_to_datetime(dados['saida'])
        qtd = dados['quantidade_pessoas']
        
        # Disponibilidade manhã
        times_manha = pd.date_range(start=entrada, end=fim_manha, freq='1H')
        for t in times_manha:
            df_disp = pd.concat([df_disp, pd.DataFrame({
                'hora': [t],
                'disponivel': [qtd],
                'jornada': [nome]
            })], ignore_index=True)
        
        # Disponibilidade tarde
        times_tarde = pd.date_range(start=inicio_tarde, end=saida, freq='1H')
        for t in times_tarde:
            df_disp = pd.concat([df_disp, pd.DataFrame({
                'hora': [t],
                'disponivel': [qtd],
                'jornada': [nome]
            })], ignore_index=True)
    
    # Agregar por hora única
    df_disp = df_disp.groupby('hora').agg({'disponivel': 'sum'}).reset_index()
    return df_disp

# Função para calcular produção (baseado em chegadas e saídas, com tempos de ciclo)
@st.cache_data
def calcular_producao(chegadas, saidas):
    df_prod = pd.DataFrame()
    
    # Processar chegadas (acumulação)
    for c in chegadas:
        h = hora_to_datetime(c['hora'])
        # Assumir produção = toneladas / tempo por tonelada (simplificado: capacidade por hora baseada em ciclo)
        # Ex: capacidade = 3600 / TEMPO_CARGA_SEG toneladas por hora por pessoa (ajustar)
        prod_hora = c['toneladas'] * (3600 / TEMPO_CARGA_SEG)  # Exemplo simplificado
        df_prod = pd.concat([df_prod, pd.DataFrame({
            'hora': [h],
            'producao': [prod_hora],
            'tipo': ['chegada']
        })], ignore_index=True)
    
    # Processar saídas (saída de carga)
    for s in saidas:
        h = hora_to_datetime(s['hora'])
        prod_hora = s['carga'] * (3600 / TEMPO_DESCARGA_SEG)  # Simplificado
        df_prod = pd.concat([df_prod, pd.DataFrame({
            'hora': [h],
            'producao': [prod_hora],
            'tipo': ['saida']
        })], ignore_index=True)
    
    # Agregar por hora
    df_prod_agg = df_prod.groupby('hora').agg({'producao': 'sum'}).reset_index()
    return df_prod_agg

# Interface principal
st.title("App Logística - Capacidade Operacional e Produtividade")

# Sidebar para configurações
st.sidebar.header("Configurações")
# Aqui pode adicionar inputs para editar jornadas, chegadas, etc.
# Por enquanto, usa dados fixos

# Abas
tab1, tab2 = st.tabs(["Gráfico Original", "Produção vs Equipe Disponível R1"])

with tab1:
    st.header("Gráfico Original (Lógica Mantida)")
    # Aqui colocaria o gráfico original - assumindo que é similar, mas sem hourly ticks extras
    disp = calcular_disponibilidade_equipe(jornadas)
    prod = calcular_producao(chegadas, saidas)
    
    # Gráfico original: pontos nas horas exatas, sem ticks hourly forçados
    fig_original = go.Figure()
    fig_original.add_trace(go.Scatter(x=disp['hora'], y=disp['disponivel'], mode='lines+markers', name='Equipe Disponível'))
    fig_original.add_trace(go.Scatter(x=prod['hora'], y=prod['producao'], mode='lines+markers', name='Produção'))
    fig_original.update_layout(title="Produção vs Equipe Disponível (Original)", xaxis_title="Hora", yaxis_title="Unidades")
    st.plotly_chart(fig_original, use_container_width=True)

with tab2:
    st.header("Produção vs Equipe Disponível R1 (Nova Aba - Temporária)")
    st.info("Esta aba mostra janelas de 1 em 1 hora no eixo X para visão completa do dia, mantendo as horas quebradas nos dados.")
    
    # Calcular dados
    disp = calcular_disponibilidade_equipe(jornadas)
    prod = calcular_producao(chegadas, saidas)
    
    # Expandir para visão hourly: criar range completo do dia (00:00 a 23:00)
    start_day = datetime(2025, 11, 12, 0, 0)
    end_day = datetime(2025, 11, 12, 23, 0)
    hourly_range = pd.date_range(start=start_day, end=end_day, freq='1H')
    
    # Reindexar disponibilidade para hourly (preencher com 0 onde não há)
    disp_hourly = disp.set_index('hora').reindex(hourly_range).fillna(0).reset_index()
    disp_hourly.columns = ['hora', 'disponivel']
    
    # Similar para produção
    prod_hourly = prod.set_index('hora').reindex(hourly_range).fillna(0).reset_index()
    prod_hourly.columns = ['hora', 'producao']
    
    # Gráfico ajustado: ticks a cada hora, dados mantidos nas posições originais (preenchidos)
    fig_r1 = go.Figure()
    fig_r1.add_trace(go.Scatter(x=disp_hourly['hora'], y=disp_hourly['disponivel'], mode='lines+markers', name='Equipe Disponível', line=dict(color='blue')))
    fig_r1.add_trace(go.Scatter(x=prod_hourly['hora'], y=prod_hourly['producao'], mode='lines+markers', name='Produção', line=dict(color='green')))
    
    # Configurar eixo X com ticks a cada hora
    fig_r1.update_xaxes(
        type='date',
        tickformat='%H:%M',
        tickmode='linear',
        dtick='M3600000',  # 1 hora em ms
        range=[start_day, end_day],
        title="Hora do Dia (Janelas de 1h)"
    )
    
    # Eixo Y customizável (exemplo)
    fig_r1.update_yaxes(title="Capacidade/Produção (Unidades/hora)")
    
    # Layout
    fig_r1.update_layout(
        title="Produção vs Equipe Disponível R1",
        hovermode='x unified',
        xaxis_rangeslider_visible=True  # Slider para navegar
    )
    
    st.plotly_chart(fig_r1, use_container_width=True)
    
    # Exemplo de renomear legendas/eixos via sidebar (para demonstrar customização)
    with st.expander("Customizar Eixos (Demonstração)"):
        novo_titulo_x = st.text_input("Título Eixo X", value="Hora do Dia (Janelas de 1h)")
        novo_titulo_y = st.text_input("Título Eixo Y", value="Capacidade/Produção (Unidades/hora)")
        if st.button("Atualizar Gráfico"):
            fig_r1.update_xaxes(title=novo_titulo_x)
            fig_r1.update_yaxes(title=novo_titulo_y)
            st.plotly_chart(fig_r1, use_container_width=True)
    
    st.markdown("**Sobre Customização:** Sim, as legendas dos eixos são totalmente customizáveis! No Plotly (usado aqui), você pode alterar títulos, labels, formatos via código ou inputs interativos como mostrado acima. Não é fixo - é flexível para renomear dinamicamente.")

# Seção adicional para relatórios/ML (placeholder para expansão)
st.header("Relatórios e Previsões")
st.write("Aqui podem ser adicionados relatórios e ML (e.g., previsão de acumulação via scikit-learn).")

# Rodapé
st.markdown("---")
st.caption("App desenvolvido com Streamlit e Plotly. Para incorporar permanentemente, remova a aba temporária.")
