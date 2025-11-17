import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np

# Simulando dados baseados na conversa (jornadas, chegadas, saídas)
data = {
    'Hora': ['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00'],
    'Chegada_Ton': [5, 15, 0, 0, 0, 0, 3, 0, 0, 0],  # Exemplo de chegadas
    'Saida_Priorizada': [0, 0, 10, 0, 5, 0, 0, 3, 0, 0],  # Saídas simuladas com prioridades
    'Equipe_Disponivel': [2, 2, 2, 2, 2, 0, 1, 1, 1, 1]  # 2 pessoas na jornada 04:30-09:30/10:30-13:26, considerando intervalo 09:30-10:30
}

df = pd.DataFrame(data)

# Calcular taxa de processamento: equipe * (3600s/hora) / (média ciclos 34s) ≈ toneladas/hora assumindo 1ton por ciclo para simplificar
tempo_ciclo_medio = (30 + 38) / 2  # 34s por operação
taxa_por_pessoa = 3600 / tempo_ciclo_medio  # Operações por hora por pessoa (assumindo 1 operação = 1ton para teste)
df['Capacidade_Hora'] = df['Equipe_Disponivel'] * taxa_por_pessoa

# Calcular acumulação cumulativa: Acumulação = Chegadas - (Saídas + Processadas), mas simplificando para acumulação pendente
df['Acumulacao'] = df['Chegada_Ton'].cumsum() - df['Saida_Priorizada'].cumsum()
df['Acumulacao'] = df['Acumulacao'].clip(lower=0)  # Não negativa

# Pré-processamento para ML: Converter hora para minutos
df['Hora_Minutos'] = pd.to_datetime(df['Hora'], format='%H:%M').dt.hour * 60 + pd.to_datetime(df['Hora'], format='%H:%M').dt.minute

# Features (entradas) e Target (previsão)
X = df[['Hora_Minutos', 'Chegada_Ton', 'Equipe_Disponivel']]
y = df['Acumulacao']

# Dividir em treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar modelo simples
model = LinearRegression()
model.fit(X_train, y_train)

# Previsão e avaliação
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f'Erro Médio Absoluto (MAE): {mae:.2f} toneladas')

# Exemplo de previsão para uma nova hora (ex.: 14:00, chegada 2ton, equipe 1)
nova_hora = np.array([[14*60, 2, 1]])  # 14:00 em minutos
previsao = model.predict(nova_hora)
print(f'Previsão de Acumulação às 14:00: {previsao[0]:.2f} toneladas')

# Gráfico simples (para visualização interativa, use plotly no app)
plt.plot(df['Hora'], df['Acumulacao'], label='Acumulação Real')
plt.xlabel('Hora')
plt.ylabel('Acumulação (ton)')
plt.title('Simulação de Acumulação de Carga')
plt.legend()
plt.show()
