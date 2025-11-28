# ================= GRÁFICO ATUALIZADO – APENAS AS MUDANÇAS QUE VOCÊ PEDIU =================
fig = go.Figure()

# Chegada (verde) e Saída (vermelho) → empilhadas quando coincidem
fig.add_trace(go.Bar(
    x=df["Horário"],
    y=df["Chegada (ton)"],
    name="Chegada",
    marker_color="#90EE90",
    opacity=0.85
))

fig.add_trace(go.Bar(
    x=df["Horário"],
    y=df["Saída (ton)"],
    name="Saída Carregada",
    marker_color="#E74C3C",
    opacity=0.85
))

# Linha da equipe (mantida igual)
fig.add_trace(go.Scatter(
    x=df["Horário"],
    y=df["Equipe_Escala"],
    mode="lines+markers",
    name="Equipe Total",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    customdata=df["Equipe Total"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# RÓTULOS FORA DA BARRA – COM CAIXINHA PEQUENA E DISCRETA (como no original, só menor)
if st.session_state.rotulos:
    for _, r in df.iterrows():
        # Chegada (+ton) → verde
        if r["Chegada (ton)"] > 0:
            fig.add_annotation(
                x=r["Horário"], y=r["Chegada (ton)"],
                text=f"+{r['Chegada (ton)']}",
                font=dict(color="#2ECC71", size=9),
                bgcolor="white",
                bordercolor="#90EE90",
                borderwidth=1,      # borda mais fina
                borderpad=2,        # caixa menor
                showarrow=False,
                yshift=10
            )
        # Saída (-ton) → vermelho (agora acima do eixo!)
        if r["Saída (ton)"] > 0:
            fig.add_annotation(
                x=r["Horário"], y=r["Saída (ton)"],
                text=f"-{r['Saída (ton)']}",
                font=dict(color="#E74C3C", size=9),
                bgcolor="white",
                bordercolor="#E74C3C",
                borderwidth=1,
                borderpad=2,
                showarrow=False,
                yshift=10           # agora acima (porque saída é positiva no eixo)
            )
        # Equipe → roxo
        if r["Equipe Total"] > 0:
            fig.add_annotation(
                x=r["Horário"], y=r["Equipe_Escala"],
                text=f"{int(r['Equipe Total'])}",
                font=dict(color="#9B59B6", size=10),
                bgcolor="white",
                bordercolor="#9B59B6",
                borderwidth=1,
                borderpad=2,
                showarrow=False,
                yshift=8
            )

# Layout atualizado – colunas empilhadas + saída positiva
fig.update_layout(
    title="Produção × Equipe Total – Saídas em Vermelho Acima + Rótulos Pequenos",
    xaxis_title="Horário",
    yaxis=dict(title="Toneladas | Equipe (escalada)", range=[0, max_ton * 1.5]),
    height=820,
    barmode="stack",  # ← empilha chegada + saída no mesmo horário
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="top", y=-0.18,
        xanchor="center", x=0.5,
        font=dict(size=12),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor="#cccccc",
        borderwidth=1
    ),
    margin=dict(l=70, r=70, t=110, b=160)
)

st.plotly_chart(fig, use_container_width=True)
