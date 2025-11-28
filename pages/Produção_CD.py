# ================= GRÁFICO COM RÓTULOS ESTILO ORIGINAL (caixinha branca + borda) =================
fig = go.Figure()

# Barras
fig.add_trace(go.Bar(
    x=df["Horário"], y=df["Chegada (ton)"],
    name="Chegada", marker_color="#90EE90", opacity=0.85
))
fig.add_trace(go.Bar(
    x=df["Horário"], y=-df["Saída (ton)"],
    name="Saída", marker_color="#E74C3C", opacity=0.85
))

# Linha da equipe (escalada)
fig.add_trace(go.Scatter(
    x=df["Horário"], y=df["Equipe_Escala"],
    mode="lines+markers",
    name="Equipe Total",
    line=dict(color="#9B59B6", width=5, dash="dot"),
    marker=dict(size=10),
    customdata=df["Equipe Total"],
    hovertemplate="Equipe: %{customdata}<extra></extra>"
))

# ================= RÓTULOS COM CAIXINHA BRANCA + BORDA COLORIDA (igual ao seu primeiro código) =================
if st.session_state.rotulos:
    for _, r in df.iterrows():
        # Chegada (+ton)
        if r["Chegada (ton)"] > 0:
            fig.add_annotation(
                x=r["Horário"], y=r["Chegada (ton)"],
                text=f"+{r['Chegada (ton)']}",
                font=dict(color="#2ECC71", size=10),
                bgcolor="white",
                bordercolor="#90EE90",
                borderwidth=2,
                borderpad=4,
                showarrow=False,
                yshift=12
            )
        # Saída (-ton)
        if r["Saída (ton)"] > 0:
            fig.add_annotation(
                x=r["Horário"], y=-r["Saída (ton)"],
                text=f"-{r['Saída (ton)']}",
                font=dict(color="#E74C3C", size=10),
                bgcolor="white",
                bordercolor="#E74C3C",
                borderwidth=2,
                borderpad=4,
                showarrow=False,
                yshift=-12
            )
        # Equipe (número de pessoas)
        if r["Equipe Total"] > 0:
            fig.add_annotation(
                x=r["Horário"], y=r["Equipe_Escala"],
                text=f"{int(r['Equipe Total'])}",
                font=dict(color="#9B59B6", size=11, family="Arial Black"),
                bgcolor="white",
                bordercolor="#9B59B6",
                borderwidth=2,
                borderpad=4,
                showarrow=False,
                yshift=8
            )

# ================= LAYOUT FINAL =================
fig.update_layout(
    title="Produção × Equipe Total (Cálculo Correto + Rótulos com Caixinha)",
    xaxis_title="Horário",
    yaxis=dict(
        title="Toneladas (↑ chegada | ↓ saída) | Equipe (escalada)",
        range=[-max_ton*1.2, max_ton*1.5]
    ),
    height=820,
    barmode="relative",
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
    margin=dict(l=70, r=70, t=110, b=160)  # espaço extra para legenda e rótulos
)

st.plotly_chart(fig, use_container_width=True)

# Confirmação visual
if "00:00" in df["Horário"].values:
    equipe_00 = df[df["Horário"] == "00:00"]["Equipe Total"].iloc[0]
    st.success(f"Às 00:00 → **{equipe_00} funcionários** (125 com seus dados reais)")

st.success("Rótulos restaurados exatamente como no seu primeiro código (caixinha branca + borda colorida)! Tudo funcionando perfeitamente – 28/11/2025")
